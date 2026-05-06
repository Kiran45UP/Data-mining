"""
Unified Signal Converters - Convert module outputs to common trading signal format
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TradeSignal:
    """Standard trading signal format"""
    date: str
    ticker: str
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0.0 to 1.0
    source: str  # 'anomaly', 'clustering', 'association'
    details: Dict[str, Any] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'date': self.date,
            'ticker': self.ticker,
            'signal': self.signal,
            'confidence': self.confidence,
            'source': self.source,
            'details': self.details or {}
        }


class AnomalySignalConverter:
    """Convert Z-score anomalies to BUY/SELL signals"""
    
    @staticmethod
    def convert(anomaly_data: Dict[str, Any], zscore_threshold: float = 2.0) -> List[TradeSignal]:
        """
        Convert anomaly detection results to signals
        Uses IsolationForest scores and daily returns
        BUY when: return < -threshold% OR (is_anomaly AND negative return)
        SELL when: return > threshold% OR (is_anomaly AND positive return)
        """
        signals = []
        ticker = anomaly_data.get('ticker', 'UNKNOWN')
        
        data_points = anomaly_data.get('data', [])
        if not data_points:
            return signals
        
        # Calculate percentile thresholds for daily returns
        returns = [p.get('daily_return', 0) for p in data_points]
        return_std = np.std(returns) if len(returns) > 1 else 0.01
        return_mean = np.mean(returns)
        
        for point in data_points:
            is_anomaly = point.get('is_anomaly', False)
            daily_return = point.get('daily_return', 0)
            anomaly_score = point.get('anomaly_score', 0)
            
            signal = None
            confidence = 0.0
            
            # Generate signal based on anomaly AND return direction
            # Also check if return is extreme relative to the distribution
            z_return = (daily_return - return_mean) / return_std if return_std > 0 else 0
            
            # Strong negative return or anomaly with negative return = BUY
            if daily_return < -0.02 or (is_anomaly and daily_return < 0):
                signal = 'BUY'
                confidence = min(abs(daily_return) / 0.05 + (0.2 if is_anomaly else 0), 1.0)
            
            # Strong positive return or anomaly with positive return = SELL
            elif daily_return > 0.02 or (is_anomaly and daily_return > 0):
                signal = 'SELL'
                confidence = min(abs(daily_return) / 0.05 + (0.2 if is_anomaly else 0), 1.0)
            
            # Pure anomaly without extreme return = neutral
            elif is_anomaly:
                # Don't generate signals for pure anomalies without return extremes
                continue
            
            if signal:
                signals.append(TradeSignal(
                    date=point['date'],
                    ticker=ticker,
                    signal=signal,
                    confidence=confidence,
                    source='anomaly',
                    details={
                        'anomaly_score': anomaly_score,
                        'daily_return': daily_return,
                        'is_anomaly': is_anomaly,
                        'z_return': round(z_return, 3)
                    }
                ))
        
        return signals


class ClusteringSignalConverter:
    """Convert clustering results to quality/risk signals"""
    
    @staticmethod
    def convert(clustering_data: Dict[str, Any], cluster_quality_threshold: float = 0.5) -> Dict[str, List[TradeSignal]]:
        """
        Convert clustering results to signals
        Strong clusters (low within-cluster variance) generate HOLD with high confidence
        Weak clusters generate HOLD with low confidence (avoid)
        Note: Clustering results don't have date information, so signals use today's date
        """
        signals_by_ticker = {}
        
        clusters = clustering_data.get('clusters', [])
        silhouette_score = clustering_data.get('silhouette_score', 0)
        
        if not clusters:
            return signals_by_ticker
        
        # Use silhouette score to determine overall quality
        quality = (silhouette_score + 1) / 2  # Normalize to 0-1
        today = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        for cluster in clusters:
            tickers = cluster.get('tickers', [])
            variance = cluster.get('variance', float('inf'))
            
            # Lower variance = stronger cluster = good quality stocks
            if variance < 1.0:  # Strong cluster
                signal_type = 'HOLD'
                confidence = min(quality, 1.0)
            else:  # Weak cluster - risky
                signal_type = 'HOLD'
                confidence = max(1 - quality, 0.3)
            
            for ticker in tickers:
                if ticker not in signals_by_ticker:
                    signals_by_ticker[ticker] = []
                
                signals_by_ticker[ticker].append(TradeSignal(
                    date=today,
                    ticker=ticker,
                    signal=signal_type,
                    confidence=confidence,
                    source='clustering',
                    details={
                        'cluster_quality': quality,
                        'variance': variance,
                        'cluster_size': len(tickers)
                    }
                ))
        
        return signals_by_ticker


class AssociationSignalConverter:
    """Convert association rules to probabilistic BUY/SELL signals"""
    
    @staticmethod
    def convert(association_data: Dict[str, Any], confidence_threshold: float = 0.6, date: str = None) -> Dict[str, List[TradeSignal]]:
        """
        Convert association rules to signals
        Extract rules involving BUY/SELL outcomes
        Use confidence as signal strength
        
        Args:
            association_data: Dict with 'rules' key containing list of rules
            confidence_threshold: Minimum confidence to generate signal
            date: Date to use for signals (defaults to today)
        """
        signals_by_ticker = {}
        
        rules = association_data.get('rules', [])
        
        if not rules:
            return signals_by_ticker
        
        if not date:
            date = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        for rule in rules:
            antecedents = rule.get('antecedents', set())
            consequents = rule.get('consequents', set())
            confidence = rule.get('confidence', 0)
            
            if confidence < confidence_threshold:
                continue
            
            # Extract ticker from antecedents (e.g., "AAPL_price_up")
            ticker = None
            for antecedent in antecedents:
                parts = str(antecedent).split('_')
                if len(parts) >= 2:
                    ticker = parts[0]
                    break
            
            if not ticker:
                continue
            
            # Determine signal from consequents
            # Look for positive price action or volume, negative price action generates sell
            signal = None
            consequents_str = str(consequents).lower()
            
            if any(x in str(c).lower() for x in ['price_up', 'volume_spike'] for c in consequents):
                signal = 'BUY'
            elif any('price_down' in str(c).lower() for c in consequents):
                signal = 'SELL'
            # If no consequent matches, treat high volume spike as BUY
            elif any('volume' in str(c).lower() for c in consequents):
                signal = 'BUY'
            
            if signal:
                if ticker not in signals_by_ticker:
                    signals_by_ticker[ticker] = []
                
                signals_by_ticker[ticker].append(TradeSignal(
                    date=date,
                    ticker=ticker,
                    signal=signal,
                    confidence=min(confidence, 1.0),
                    source='association',
                    details={
                        'rule_confidence': confidence,
                        'antecedents': str(list(antecedents)),
                        'consequents': str(list(consequents))
                    }
                ))
        
        return signals_by_ticker



class SignalAggregator:
    """Combine signals from multiple sources and apply custom rules"""
    
    @staticmethod
    def aggregate_signals(signals: List[TradeSignal], aggregation_method: str = 'weighted') -> Dict[str, Dict]:
        """
        Aggregate signals by ticker and date
        Returns combined signal with confidence score
        """
        signal_map = {}
        
        for signal in signals:
            key = (signal.date, signal.ticker)
            if key not in signal_map:
                signal_map[key] = {
                    'date': signal.date,
                    'ticker': signal.ticker,
                    'signals': [],
                    'sources': set()
                }
            
            signal_map[key]['signals'].append(signal)
            signal_map[key]['sources'].add(signal.source)
        
        # Aggregate
        aggregated = {}
        for key, data in signal_map.items():
            signals_list = data['signals']
            
            if aggregation_method == 'weighted':
                # Weight signals by confidence
                buy_score = sum(s.confidence for s in signals_list if s.signal == 'BUY')
                sell_score = sum(s.confidence for s in signals_list if s.signal == 'SELL')
                hold_score = sum(s.confidence for s in signals_list if s.signal == 'HOLD')
                
                total_score = buy_score + sell_score + hold_score
                if total_score == 0:
                    final_signal = 'HOLD'
                    confidence = 0.0
                else:
                    if buy_score > sell_score and buy_score > hold_score:
                        final_signal = 'BUY'
                        confidence = buy_score / total_score
                    elif sell_score > buy_score and sell_score > hold_score:
                        final_signal = 'SELL'
                        confidence = sell_score / total_score
                    else:
                        final_signal = 'HOLD'
                        confidence = hold_score / total_score
            
            elif aggregation_method == 'unanimous':
                # All signals must agree
                signal_types = set(s.signal for s in signals_list)
                if len(signal_types) == 1:
                    final_signal = signal_types.pop()
                    confidence = np.mean([s.confidence for s in signals_list])
                else:
                    final_signal = 'HOLD'
                    confidence = 0.0
            
            else:  # 'majority'
                signal_counts = {}
                for s in signals_list:
                    signal_counts[s.signal] = signal_counts.get(s.signal, 0) + 1
                
                final_signal = max(signal_counts.items(), key=lambda x: x[1])[0]
                confidence = np.mean([s.confidence for s in signals_list])
            
            aggregated[key] = {
                'date': data['date'],
                'ticker': data['ticker'],
                'signal': final_signal,
                'confidence': round(confidence, 3),
                'source_count': len(data['sources']),
                'sources': list(data['sources']),
                'signals': [{'signal': s.signal, 'confidence': s.confidence, 'source': s.source} for s in signals_list]
            }
        
        return aggregated
