from typing import Dict, List

from .models import Cluster, Recommendation


class RecommendationEngine:
    def recommend(self, cluster: Cluster) -> List[Recommendation]:
        recommendations: List[Recommendation] = []
        if cluster.pattern_name == "Bruteforcer":
            recommendations.append(
                Recommendation(
                    type="IP lockout",
                    priority="CRITICAL",
                    params={"duration_minutes": 30, "max_attempts": 5},
                    explanation="Bloquer temporairement l'IP après des tentatives de connexion répétées pour limiter le bruteforce.",
                )
            )
            recommendations.append(
                Recommendation(
                    type="CAPTCHA adaptatif",
                    priority="HIGH",
                    params={"trigger": "failed_logins", "min_failures": 3},
                    explanation="Ajouter un CAPTCHA adaptatif pour les sessions mobiles suspectes sur /login, /auth et /signin.",
                )
            )
        if cluster.pattern_name == "API_Scanner":
            recommendations.append(
                Recommendation(
                    type="Rate-limiting",
                    priority="HIGH",
                    params={"requests_per_minute": 20},
                    explanation="Limiter le nombre d'endpoints différents par IP pour réduire la collecte automatisée d'API.",
                )
            )
            recommendations.append(
                Recommendation(
                    type="Behavioral tracking",
                    priority="MEDIUM",
                    params={"flag": "endpoint_variation"},
                    explanation="Suivre le comportement des clients qui parcourent de nombreuses routes pour détecter des scans furtifs.",
                )
            )
        if cluster.pattern_name == "Bot_Scraper":
            recommendations.append(
                Recommendation(
                    type="CORS restriction",
                    priority="MEDIUM",
                    params={"allowed_origins": ["https://trusted.app"]},
                    explanation="Restreindre les origines autorisées pour diminuer les requêtes automatisées externes.",
                )
            )
            recommendations.append(
                Recommendation(
                    type="Rate-limiting",
                    priority="HIGH",
                    params={"requests_per_minute": 15},
                    explanation="Appliquer des limites de taux pour éviter les rafales de requêtes automatisées.",
                )
            )
        if cluster.pattern_name == "Legitimate_Traffic":
            recommendations.append(
                Recommendation(
                    type="Behavioral tracking",
                    priority="LOW",
                    params={"flag": "normal_mobile_activity"},
                    explanation="Surveiller le trafic mobile normal pour affiner les règles de détection sans bloquer les utilisateurs légitimes.",
                )
            )
        if not recommendations:
            recommendations.append(
                Recommendation(
                    type="Rate-limiting",
                    priority="MEDIUM",
                    params={"requests_per_minute": 40},
                    explanation="Appliquer une protection générale pour limiter les abus tout en préservant l'expérience utilisateur.",
                )
            )
        return recommendations
