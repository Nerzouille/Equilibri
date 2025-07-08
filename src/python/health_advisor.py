import ollama
import json
from typing import Dict, List, Tuple, Optional
from ml_health_scorer import MLHealthScorer

class HealthAdvisor:
    """LLM-powered health advisor that provides personalized advice based on ML scores"""

    def __init__(self, model_name: str = "llama3:8b"):
        self.model_name = model_name
        self.client = ollama.Client()

    def analyze_health_day(self, health_data: Dict, health_score: float, 
                          user_profile: str = "balanced") -> Dict:
        """
        Analyze a day's health data and provide personalized insights

        Args:
            health_data: Raw health metrics for the day
            health_score: ML-calculated health score (0-100)
            user_profile: User personality for tone adaptation

        Returns:
            Dict with analysis, suggestions, and tone-appropriate messaging
        """

        # Calculate sub-scores for detailed analysis
        sub_scores = self._calculate_sub_scores(health_data)

        # Generate personalized prompt
        prompt = self._build_analysis_prompt(health_data, health_score, sub_scores, user_profile)

        # Get LLM response
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                "temperature": 0.7,  # Slightly creative but consistent
                "num_predict": 200,  # Concise responses
            }
        )

        # Parse and structure response
        return self._parse_llm_response(response['response'], health_score, sub_scores)

    def _calculate_sub_scores(self, health_data: Dict) -> Dict:
        """Calculate sub-scores for each health category"""
        sub_scores = {}

        # Sleep score (0-100)
        sleep_hours = health_data.get('sleep_hours', 7)
        if 7 <= sleep_hours <= 9:
            sub_scores['sleep'] = 90
        elif 6 <= sleep_hours <= 10:
            sub_scores['sleep'] = 75
        elif sleep_hours < 5:
            sub_scores['sleep'] = 30
        else:
            sub_scores['sleep'] = 60

        # Activity score (0-100)
        steps = health_data.get('steps', 5000)
        if steps >= 10000:
            sub_scores['activity'] = 95
        elif steps >= 8000:
            sub_scores['activity'] = 80
        elif steps >= 5000:
            sub_scores['activity'] = 60
        else:
            sub_scores['activity'] = 30

        # Hydration score (0-100) - FIXED
        hydration = health_data.get('hydration_liters', 2.0)
        if 2.0 <= hydration <= 3.5:
            sub_scores['hydration'] = 95
        elif 1.5 <= hydration <= 4.0:
            sub_scores['hydration'] = 85
        elif hydration >= 4.0:
            sub_scores['hydration'] = 75  # Très bien mais peut-être trop
        else:
            sub_scores['hydration'] = 40

        # Stress score (0-100)
        stress_level = health_data.get('stress_level', 'medium')
        stress_map = {'low': 90, 'medium': 60, 'high': 25}
        sub_scores['stress'] = stress_map.get(stress_level, 60)

        # Screen time score (0-100)
        screen_time = health_data.get('screen_time_hours', 5)
        if screen_time <= 4:
            sub_scores['screen_time'] = 90
        elif screen_time <= 6:
            sub_scores['screen_time'] = 70
        elif screen_time <= 8:
            sub_scores['screen_time'] = 50
        else:
            sub_scores['screen_time'] = 25

        return sub_scores

    def _build_analysis_prompt(self, health_data: Dict, health_score: float,
                              sub_scores: Dict, user_profile: str) -> str:
        """Build personalized prompt for LLM analysis"""

        # Find the actual weakest area that needs improvement
        areas_needing_improvement = {k: v for k, v in sub_scores.items() if v < 70}

        if areas_needing_improvement:
            weakest_area = min(areas_needing_improvement, key=areas_needing_improvement.get)
            weakest_score = areas_needing_improvement[weakest_area]
        else:
            weakest_area = min(sub_scores, key=sub_scores.get)
            weakest_score = sub_scores[weakest_area]

        # Define personality traits for different profiles
        personality_traits = {
            "balanced": "encouraging and balanced",
            "motivated": "energetic and motivating",
            "calm": "gentle and supportive",
            "direct": "straightforward and practical",
            "humorous": "light-hearted with gentle humor"
        }

        tone = personality_traits.get(user_profile, "encouraging and balanced")

        prompt = f"""You are a health coach. Analyze this person's health data logically.

HEALTH DATA:
- Overall Score: {health_score}/100
- Sleep: {health_data.get('sleep_hours', 'N/A')}h (score: {sub_scores.get('sleep', 'N/A')}/100)
- Steps: {health_data.get('steps', 'N/A')} (score: {sub_scores.get('activity', 'N/A')}/100)
- Hydration: {health_data.get('hydration_liters', 'N/A')}L (score: {sub_scores.get('hydration', 'N/A')}/100)
- Stress: {health_data.get('stress_level', 'N/A')} (score: {sub_scores.get('stress', 'N/A')}/100)
- Screen Time: {health_data.get('screen_time_hours', 'N/A')}h (score: {sub_scores.get('screen_time', 'N/A')}/100)

PERSONALITY: Be {tone} in your response.

IMPORTANT GUIDELINES:
- 2-3.5L hydration is EXCELLENT (scores 85-95/100) - DON'T suggest more water
- 7-9h sleep is optimal
- 8000+ steps is good, 10000+ is excellent
- Only suggest improvements for areas scoring below 70/100

Your lowest scoring area is: {weakest_area} ({weakest_score}/100)

Please provide:
1. Brief analysis acknowledging what's going well
2. Focus ONLY on the area that needs improvement (score < 70)
3. One specific, actionable tip for tomorrow

Don't suggest improving things that are already excellent."""

        return prompt

    def _parse_llm_response(self, response: str, health_score: float, sub_scores: Dict) -> Dict:
        """Parse LLM response into structured format"""

        # Find weakest area for priority suggestion
        areas_needing_improvement = {k: v for k, v in sub_scores.items() if v < 70}

        if areas_needing_improvement:
            weakest_area = min(areas_needing_improvement, key=areas_needing_improvement.get)
        else:
            weakest_area = min(sub_scores, key=sub_scores.get)

        return {
            "health_score": health_score,
            "sub_scores": sub_scores,
            "analysis": response.strip(),
            "priority_area": weakest_area,
            "priority_score": sub_scores[weakest_area],
            "timestamp": self._get_timestamp()
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_morning_recommendations(self, health_data: Dict, health_score: float) -> List[str]:
        """Generate 3 specific morning recommendations"""

        prompt = f"""Based on yesterday's health data, give 3 specific morning recommendations.

YESTERDAY'S DATA:
- Health Score: {health_score}/100
- Sleep: {health_data.get('sleep_hours')}h
- Steps: {health_data.get('steps')}
- Hydration: {health_data.get('hydration_liters')}L
- Stress: {health_data.get('stress_level')}

IMPORTANT:
- If hydration is 2L+ that's GOOD, don't suggest more water
- Focus on actual problem areas

Format as a simple numbered list:
1. [specific action for morning]
2. [specific action for morning]
3. [specific action for morning]

Keep each recommendation to one sentence and actionable."""

        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            options={"temperature": 0.6, "num_predict": 150}
        )

        # Parse numbered list
        recommendations = []
        for line in response['response'].split('\n'):
            if line.strip() and (line.strip().startswith(('1.', '2.', '3.'))):
                recommendations.append(line.strip()[2:].strip())

        return recommendations[:3]  # Ensure max 3 recommendations
