import json
from nlp_logic import StanceClassifier
from stance_analyzer import classify_text_enhanced, STANCE_OPPONENT_ANTIWAR

def test_examples():
    nlp = StanceClassifier(device=-1)
    
    examples = [
        {
            "name": "Katie Halper",
            "text": "Tues 7pm EST @DemSocialists organizers @katewillett & @dvaldesnyc talk @codepink Cuba Convoy. @WOLPalestine's @NerdeenKiswani talks about suing Betar under KKK Act. Iranian analyst @SinaToossi talks Iran"
        },
        {
            "name": "Max Blumenthal",
            "text": "The Ellisons are advancing the 8th front of Israel's wars: an assault on the minds of Americans through an unprecedented media takeover. As Greater Israel's crimes escalate, these oligarchs are working to establish an information dictatorship that drowns out all critical voices"
        },
        {
            "name": "Ro Khanna",
            "text": "Ro Khanna asks what happened to pro-peace MAGA: 'There could not have been a more dishonest campaign in modern history than Trump and Vance pretending to be the pro-peace candidates. They said Kamala Harris would get us into a war in Iran. What happened to all that?'"
        },
        {
            "name": "Bernie Sanders",
            "text": "The United States gave Netanyahu over $24 billion in taxpayer dollars to fund his horrific war in Gaza. That wasn't enough. Netanyahu wanted war with Iran. Trump gave him one. The American people should determine U.S. foreign policy."
        },
        {
            "name": "Neutral/Irrelevant",
            "text": "Just had a great dinner with friends in New York. The weather is amazing today!"
        }
    ]

    print("\n" + "="*80)
    print("🔍 VERIFYING STANCE CLASSIFICATION EXAMPLES")
    print("="*80 + "\n")

    for ex in examples:
        stance, direct_match, scores = classify_text_enhanced(ex["text"], nlp)
        print(f"👤 Target: {ex['name']}")
        print(f"📝 Text: {ex['text'][:100]}...")
        print(f"🛡️  Stance: {stance}")
        print(f"🔑 Key/Method: {direct_match}")
        if scores:
            print(f"📊 Scores: Neg={scores.get('sentiment',{}).get('NEGATIVE',0):.2f}, Tox={scores.get('toxicity',0):.2f}, Boost={scores.get('rule_attack_boost',0):.2f}")
        print("-" * 40)

if __name__ == "__main__":
    test_examples()
