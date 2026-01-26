import numpy as np


def cosine_similarity(embedding1, embedding2):
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def get_percentage(cosine_score, threshold=0.5):
    """
    Cosine similarity natijasini foizga aylantiradi.
    
    Args:
        cosine_score (float): Model qaytargan qiymat (0.0 dan 1.0 gacha)
        threshold (float): Tanish/notanish chegarasi (default: 0.5)
    
    Returns:
        float: Foiz qiymati (0.0 dan 100.0 gacha)
    
    Logika:
        - threshold dan yuqori: 90-100% oralig'ida (tanish)
        - threshold dan past: 0-89% oralig'ida (notanish)
    """
    # Cosine score qiymatini tekshirish
    cosine_score = max(0.0, min(1.0, cosine_score))
    
    if cosine_score >= threshold:
        # Threshold dan yuqori: [threshold, 1.0] -> [90%, 100%]
        # Formula: linear interpolation (chiziqli interpolyatsiya)
        percentage = ((cosine_score - threshold) / (1.0 - threshold)) * 10.0 + 90.0
    else:
        # Threshold dan past: [0.0, threshold] -> [0%, 89%]
        percentage = (cosine_score / threshold) * 89.0
    
    return round(percentage, 2)