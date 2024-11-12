
from app import app
from db import db
from models import (
    User, LearningPath, Module, Resource, Feedback, Leaderboard,
    QuizContent, QuizSubmission, Achievement, Challenge, Reply,
    UserAchievement, UserChallenge, UserLearningPath, ModuleResource
)
from datetime import datetime, timedelta
from random import randint, choice
from werkzeug.security import generate_password_hash

with app.app_context():
    # Reset database
    db.delete_all()
    db.create_all()

    # Seed Users
    users = []
    roles = ["Admin", "Contributor", "Learner"]
    for i in range(1, 21):
        user = User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password_hash=generate_password_hash("password"),
            role=choice(roles),
            points=randint(0, 1000),
            date_joined=datetime.now() - timedelta(days=randint(1, 365))
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    # Seed Learning Paths
    learning_paths = []
    for i in range(1, 21):
        learning_path = LearningPath(
            title=f"Learning Path {i}",
            description=f"Description of learning path {i}",
            contributor_id=choice(users).user_id,
            rating=randint(1, 5)
        )
        learning_paths.append(learning_path)
    db.session.add_all(learning_paths)
    db.session.commit()

    # Seed Modules
    modules = []
    for i in range(1, 21):
        module = Module(
            title=f"Module {i}",
            description=f"Description of module {i}",
            learning_path_id=choice(learning_paths).learning_path_id
        )
        modules.append(module)
    db.session.add_all(modules)
    db.session.commit()

    # Seed Resources
    resource_types = ["Video", "Article", "Tutorial"]
    resources = []
    for i in range(1, 21):
        resource = Resource(
            title=f"Resource {i}",
            url=f"http://example.com/resource{i}",
            type=choice(resource_types),
            description=f"Description of resource {i}",
            contributor_id=choice(users).user_id
        )
        resources.append(resource)
    db.session.add_all(resources)
    db.session.commit()

    # Seed Feedback
    feedbacks = []
    for i in range(1, 21):
        feedback = Feedback(
            user_id=choice(users).user_id,
            resource_id=choice(resources).resource_id,
            comment=f"Feedback comment {i}",
            rating=randint(1, 5)
        )
        feedbacks.append(feedback)
    db.session.add_all(feedbacks)
    db.session.commit()

    # Seed Leaderboard
    leaderboards = []
    for user in users:
        leaderboard = Leaderboard(
            user_id=user.user_id,
            score=randint(0, 1000)
        )
        leaderboards.append(leaderboard)
    db.session.add_all(leaderboards)
    db.session.commit()

    # Seed QuizContent
    #how to include the parent id
    quiz_contents = []
    for i in range(1, 21):
        quiz_content = QuizContent(
            module_id=choice(modules).module_id,
            
            type="Multiple Choice",
            content_text=f"Question {i}?",
            points=randint(5, 20),
            is_correct=choice([True, False]),
            created_at=datetime.now() - timedelta(days=randint(1, 100))
        )
        quiz_contents.append(quiz_content)
    db.session.add_all(quiz_contents)
    db.session.commit()

    # Seed QuizSubmission
    quiz_submissions = []
    for i in range(1, 21):
        quiz_submission = QuizSubmission(
            user_id=choice(users).user_id,
            quiz_id=choice(quiz_contents).id,
            score=randint(0, 100),
            submitted_at=datetime.now() - timedelta(days=randint(1, 100))
        )
        quiz_submissions.append(quiz_submission)
    db.session.add_all(quiz_submissions)
    db.session.commit()

    # Seed Achievements
    achievements = []
    for i in range(1, 21):
        achievement = Achievement(
            name=f"Achievement {i}",
            description=f"Description for achievement {i}",
            icon_url=f"http://example.com/icon{i}.png",
            points_required=randint(50, 500),
            created_at=datetime.now() - timedelta(days=randint(1, 365))
        )
        achievements.append(achievement)
    db.session.add_all(achievements)
    db.session.commit()

    # Seed Challenges
    challenges = []
    for i in range(1, 21):
        challenge = Challenge(
            title=f"Challenge {i}",
            description=f"Description of challenge {i}",
            points_reward=randint(10, 100),
            start_date=datetime.now() - timedelta(days=randint(10, 365)),
            end_date=datetime.now() + timedelta(days=randint(10, 365))
        )
        challenges.append(challenge)
    db.session.add_all(challenges)
    db.session.commit()

    # Seed Comments
    # comments = []
    # for i in range(1, 21):
    #     comment = Comment(
    #         user_id=choice(users).user_id,
    #         content=f"Comment content {i}",
    #         created_at=datetime.now() - timedelta(days=randint(1, 365)),
    #         updated_at=datetime.now()
    #     )
    #     comments.append(comment)
    # db.session.add_all(comments)
    # db.session.commit()

    # Seed Replies
    replies = []
    for i in range(1, 21):
        reply = Reply(
            user_id=choice(users).user_id,
            feedback_id=choice(feedback).id,
            content=f"Reply content {i}",
            created_at=datetime.now() - timedelta(days=randint(1, 365)),
            updated_at=datetime.now()
        )
        replies.append(reply)
    db.session.add_all(replies)
    db.session.commit()

    # Seed Join Tables
    # ModuleResource
    module_resources = []
    for i in range(1, 21):
        module_resource = ModuleResource(
            module_id=choice(modules).module_id,
            resource_id=choice(resources).resource_id,
            added_at=datetime.now() - timedelta(days=randint(1, 365))
        )
        module_resources.append(module_resource)
    db.session.add_all(module_resources)
    db.session.commit()

    # UserAchievement
    user_achievements = []
    for i in range(1, 21):
        user_achievement = UserAchievement(
            user_id=choice(users).user_id,
            achievement_id=choice(achievements).id,
            earned_at=datetime.now() - timedelta(days=randint(1, 365))
        )
        user_achievements.append(user_achievement)
    db.session.add_all(user_achievements)
    db.session.commit()

    # UserLearningPath
    user_learning_paths = []
    for i in range(1, 21):
        user_learning_path = UserLearningPath(
            user_id=choice(users).user_id,
            learning_path_id=choice(learning_paths).learning_path_id,
            progress_percentage=randint(0, 100),
            last_accessed=datetime.now() - timedelta(days=randint(1, 365)),
            started_at=datetime.now() - timedelta(days=randint(1, 365)),
            completed_at=datetime.now() if randint(0, 1) else None
        )
        user_learning_paths.append(user_learning_path)
    db.session.add_all(user_learning_paths)
    db.session.commit()

    # UserChallenge
    user_challenges = []
    for i in range(1, 21):
        user_challenge = UserChallenge(
            user_id=choice(users).user_id,
            challenge_id=choice(challenges).id,
            completed_at=datetime.now() if randint(0, 1) else None
        )
        user_challenges.append(user_challenge)
    db.session.add_all(user_challenges)
    db.session.commit()

    print("Database seeded with extended sample data!")
