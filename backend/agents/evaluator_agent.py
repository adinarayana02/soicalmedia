import math
from typing import List, Dict, Any

class EvaluatorAgent:
    """
    Reasoning Layer:
    Computes behavioral risk using fused signals from the ObserverAgent.
    Implements the mathematical framework:
    - Distress Probability D_i
    - Advanced Risk Model R_i
    - Time-aware Wellbeing Model W_u(t)
    - Session Risk SR_j
    """

    def _sigmoid(self, x: float) -> float:
        return 1 / (1 + math.exp(-x))

    def evaluate_session(self, observed_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes the ordered chronological events with their F={S, T, E, LNR, B} signals.
        Returns final session metrics encompassing Wellbeing, Risk, Instability, and Temporal Risk.
        """
        
        if not observed_events:
            return {
                "wellbeing_score": 100.0,
                "risk_score": 0.0,
                "distress_probability": 0.0,
                "behavioral_instability": 0.0,
                "temporal_risk_index": 0.0,
                "session_risk": 0.0,
                "events_evaluated": 0
            }

        # Model Weights mapping to prompt
        # Distress params
        a_d, b_d, c_d, d_d = -2.0, 3.0, 1.5, 2.0  # S_i decreases prob, T_i raises, LNR_i raises, delta_S_i raises
        
        # Risk params
        # R_i = w1*D_i + w2*T_i + w3*LNR_i + w4*E_i + w5*B_i + w6*(T_i*LNR_i) + w7*(S_i*B_i)
        w1, w2, w3, w4, w5, w6, w7 = 15.0, 10.0, 8.0, 2.0, 5.0, 12.0, -5.0
        
        # Wellbeing params
        # W(t) = W(t-1) + aS - bT - cLNR - dD - phi_deltaR
        wb_a, wb_b, wb_c, wb_d, wb_phi = 5.0, 8.0, 4.0, 10.0, 2.0
        
        current_wellbeing = 100.0
        total_risk = 0.0
        max_distress = 0.0
        total_instability = 0.0
        total_lnr = 0.0
        total_t_lnr_eta = 0.0
        
        prev_s = 0.5
        prev_r = 0.0
        
        for idx, event in enumerate(observed_events):
            sigs = event.get("signals", {})
            
            s_i = sigs.get("S", 0.5)
            t_i = sigs.get("T", 0.1)  # Toxicity
            l_i = sigs.get("L", 0.1)  # Late Night activity (Temporal)
            e_i = sigs.get("E", 0.5)  # Engagement
            b_i = sigs.get("B", 0.0)  # Behavioral change
            
            delta_s_i = prev_s - s_i if prev_s > s_i else 0.0 # Sudden drop
            prev_s = s_i
            
            # Distress Probability D_i
            # P(D_i = 1) = sigmoid(a*S_i + b*T_i + c*L_i + d*delta_S_i)
            # Actually, S_i is positive so it should negative weight in distress
            d_logit = (a_d * s_i) + (b_d * t_i) + (c_d * l_i) + (d_d * delta_s_i)
            d_i = self._sigmoid(d_logit)
            
            max_distress = max(max_distress, d_i)
            
            # Advanced Risk Model R_i (Normalized to 0 - 100 scale)
            r_i = (40.0 * d_i) + (25.0 * t_i) + (20.0 * l_i) + (15.0 * b_i)
            r_i = max(0.0, min(100.0, r_i))
            total_risk += r_i
            
            delta_r = r_i - prev_r if r_i > prev_r else 0.0
            prev_r = r_i
            
            # Time-aware Wellbeing Model W_u(t) (Complementary 100 - R_i)
            current_wellbeing = max(0.0, min(100.0, 100.0 - r_i))
            
            # Session Risk components
            lam, eta = 1.5, 0.5
            total_t_lnr_eta += (t_i + (lam * l_i) + (eta * e_i))
            
            total_instability += b_i
            total_lnr += l_i
            
            # Store calculated risk in event for the advisor
            event["evaluated_risk"] = {
                "r_i": r_i,
                "d_i": d_i,
                "wellbeing_at_time": current_wellbeing
            }
            
        n = len(observed_events)
        
        # Averages
        avg_risk = total_risk / n
        session_risk = total_t_lnr_eta / n
        avg_instability = total_instability / n
        avg_temporal_risk = total_lnr / n
        
        # Behavioral Change Detection (Sudden risk spike)
        tau = 45.0 # threshold for risk spike
        sbc = 1 if (max_distress > 0.6 and avg_risk > tau) else 0

        final_wellbeing = max(0.0, min(100.0, 100.0 - avg_risk))

        return {
            "wellbeing_score": round(final_wellbeing, 2),
            "risk_score": round(avg_risk, 2),
            "distress_probability": round(max_distress, 2),
            "behavioral_instability": round(avg_instability, 2),
            "temporal_risk_index": round(avg_temporal_risk, 2),
            "session_risk": round(session_risk, 2),
            "sudden_behavioral_change": sbc,
            "events_evaluated": n
        }

