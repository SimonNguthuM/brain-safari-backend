from app import app
from db import db
from datetime import datetime
from models import (User, LearningPath, Module, Resource, Feedback, Comment, Reply, 
                    Challenge, Achievement, Leaderboard, ModuleResource, UserAchievement, 
                    UserLearningPath, UserChallenge, QuizContent, QuizSubmission)
from faker import Faker
import random

fake = Faker()

def seed_database():
    db.drop_all()
    db.create_all()

    users = []
    for _ in range(10):
        username = fake.user_name()
        email = fake.email()
        role = random.choice(["Admin", "Learner", "Contributor"])
        password = fake.password()
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        users.append(user)

    db.session.commit()

    learning_path1 = LearningPath(title="Python Basics", description="Introduction to Python", contributor_id=users[2].id)
    learning_path2 = LearningPath(title="Data Science", description="Data Science path with Python and Machine Learning", contributor_id=users[3].id)

    db.session.add_all([learning_path1, learning_path2])
    db.session.commit()

    module1 = Module(title="Introduction to Python", description="Learn Python basics", learning_path_id=learning_path1.id)
    module2 = Module(title="Data Analysis", description="Learn data analysis techniques", learning_path_id=learning_path2.id)

    db.session.add_all([module1, module2])
    db.session.commit()

    resources = []
    resource1 = Resource(title="Python Documentation", url="https://docs.python.org", type="Article", description="Official Python docs", contributor_id=users[3].id)
    resource2 = Resource(title="Pandas Tutorial", url="https://pandas.pydata.org", type="Tutorial", description="Learn Pandas for data manipulation", contributor_id=users[3].id)

    resources.extend([resource1, resource2])
    db.session.add_all(resources)
    db.session.commit()

    module_resource1 = ModuleResource(module_id=module1.id, resource_id=resource1.id)
    module_resource2 = ModuleResource(module_id=module2.id, resource_id=resource2.id)
    
    db.session.add_all([module_resource1, module_resource2])
    db.session.commit()

    feedbacks = []
    for resource in resources:
        for user in users:
            comment = fake.sentence()
            rating = random.randint(1, 5)
            feedback = Feedback(user_id=user.id, resource_id=resource.id, comment=comment, rating=rating)
            feedbacks.append(feedback)

    db.session.add_all(feedbacks)
    db.session.commit()

    achievement1 = Achievement(name="Python Novice", description="Complete the Python Basics path", points_required=100, icon_url="icon_url_1")
    achievement2 = Achievement(name="Data Scientist", description="Complete Data Science path", points_required=200, icon_url="icon_url_2")

    db.session.add_all([achievement1, achievement2])
    db.session.commit()

    user_achievement1 = UserAchievement(user_id=users[0].id, achievement_id=achievement1.id)
    user_achievement2 = UserAchievement(user_id=users[1].id, achievement_id=achievement2.id)
    
    db.session.add_all([user_achievement1, user_achievement2])
    db.session.commit()

    challenge1 = Challenge(title="Complete Module 1", description="Complete the first module", points_reward=10, start_date=datetime.utcnow(), end_date=datetime.utcnow())
    challenge2 = Challenge(title="Finish Python Basics", description="Finish the Python Basics path", points_reward=20, start_date=datetime.utcnow(), end_date=datetime.utcnow())

    db.session.add_all([challenge1, challenge2])
    db.session.commit()

    user_learning_paths = []
    for user in users:
        progress = random.randint(0, 100)
        user_learning_path = UserLearningPath(user_id=user.id, learning_path_id=learning_path1.id, progress_percentage=progress, started_at=datetime.utcnow())
        user_learning_paths.append(user_learning_path)

    db.session.add_all(user_learning_paths)
    db.session.commit()

    user_challenges = []
    for user in users:
        challenge = UserChallenge(user_id=user.id, challenge_id=challenge1.id)
        user_challenges.append(challenge)

    db.session.add_all(user_challenges)
    db.session.commit()

    leaderboard_entries = []
    for user in users[:8]:
        score = random.randint(50, 150)
        leaderboard_entry = Leaderboard(user_id=user.id, score=score)
        leaderboard_entries.append(leaderboard_entry)

    db.session.add_all(leaderboard_entries)
    db.session.commit()

    for user in users[:8]:
        user.add_points(random.randint(50, 150))

    quiz_contents = []
    quiz1 = QuizContent(module_id=module1.id, type="quiz", content_text="What is Python?", points=10)
    question1 = QuizContent(module_id=module1.id, type="question", content_text="What is Python used for?", points=5)
    option1 = QuizContent(module_id=module1.id, type="option", content_text="Programming Language", is_correct=True)

    quiz_contents.extend([quiz1, question1, option1])
    db.session.add_all(quiz_contents)
    db.session.commit()

    quiz_submissions = []
    for user in users[:8]:
        quiz_submission = QuizSubmission(user_id=user.id, quiz_id=quiz1.id, score=random.randint(0, 10))
        quiz_submissions.append(quiz_submission)

    db.session.add_all(quiz_submissions)
    db.session.commit()

    for resource in resources:
        for user in users:
            comment_content = fake.sentence()
            comment = Comment(user_id=user.id, content=comment_content)
            db.session.add(comment)

    db.session.commit()

    comments = Comment.query.all()
    for comment in comments:
        for user in users:
            reply_content = fake.sentence()
            reply = Reply(user_id=user.id, comment_id=comment.id, content=reply_content)
            db.session.add(reply)

    db.session.commit()

    print("Database seeded successfully.")

if __name__ == "__main__":
    with app.app_context():
        seed_database()
