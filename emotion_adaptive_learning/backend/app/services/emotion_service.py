def fuse_multimodal(facial, speech, typing):

    emotion_votes = {}

    for emotion in [facial, speech, typing]:
        emotion_votes[emotion] = emotion_votes.get(emotion, 0) + 1

    return max(emotion_votes, key=emotion_votes.get)
