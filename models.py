from db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin

class User(db.Model, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Admin, Contributor, Learner
    points = db.Column(db.Integer, default=0)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    leaderboard_entry = db.relationship('Leaderboard', back_populates='user', uselist=False)
    feedback = db.relationship('Feedback', back_populates='user')
    comments = db.relationship('Comment', back_populates='user')
    replies = db.relationship('Reply', back_populates='user')
    enrolled_paths = db.relationship('UserLearningPath', back_populates='user')
    challenges = db.relationship('UserChallenge', back_populates='user')
    achievements = db.relationship('UserAchievement', back_populates='user')
    quiz_submissions = db.relationship('QuizSubmission', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class LearningPath(db.Model, SerializerMixin):
    __tablename__ = 'learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer)

    # Relationships
    modules = db.relationship('Module', back_populates='learning_path')
    enrolled_users = db.relationship('UserLearningPath', back_populates='learning_path')
    contributor = db.relationship('User', back_populates='enrolled_paths')

    def __repr__(self):
        return f"<LearningPath(id={self.id}, title={self.title})>"


class Module(db.Model, SerializerMixin):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))

    # Relationships
    learning_path = db.relationship('LearningPath', back_populates='modules')
    resources = db.relationship('ModuleResource', back_populates='module')
    challenges = db.relationship('Challenge', back_populates='module')
    quiz_content = db.relationship('QuizContent', back_populates='module')

    def __repr__(self):
        return f"<Module(id={self.id}, title={self.title})>"


class Resource(db.Model, SerializerMixin):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(200))
    type = db.Column(db.Enum('Video', 'Article', 'Tutorial', name='resource_type'))
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    feedbacks = db.relationship('Feedback', back_populates='resource')
    modules = db.relationship('ModuleResource', back_populates='resource')

    def __repr__(self):
        return f"<Resource(id={self.id}, title={self.title})>"


class Feedback(db.Model, SerializerMixin):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)

    # Relationships
    user = db.relationship("User", back_populates="feedback")
    resource = db.relationship("Resource", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback(id={self.id}, user_id={self.user_id}, rating={self.rating})>"


class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="comments")
    replies = db.relationship("Reply", back_populates="comment")

    def __repr__(self):
        return f"<Comment(id={self.id}, content='{self.content[:20]}...')>"


class Reply(db.Model, SerializerMixin):
    __tablename__ = 'replies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="replies")
    comment = db.relationship("Comment", back_populates="replies")

    def __repr__(self):
        return f"<Reply(id={self.id}, content='{self.content[:20]}...')>"


class Challenge(db.Model, SerializerMixin):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    points_reward = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))

    # Relationships
    module = db.relationship("Module", back_populates="challenges")
    users = db.relationship("UserChallenge", back_populates="challenge")

    def __repr__(self):
        return f"<Challenge(id={self.id}, title={self.title})>"


class Achievement(db.Model, SerializerMixin):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(200))
    points_required = db.Column(db.Integer)

    # Relationships
    users = db.relationship("UserAchievement", back_populates="achievement")

    def __repr__(self):
        return f"<Achievement(id={self.id}, name={self.name})>"


class Leaderboard(db.Model, SerializerMixin):
    __tablename__ = 'leaderboards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.Integer, default=0)

    # Relationships
    user = db.relationship("User", back_populates="leaderboard_entry")

    def __repr__(self):
        return f"<Leaderboard(id={self.id}, score={self.score})>"


class ModuleResource(db.Model, SerializerMixin):
    __tablename__ = 'module_resources'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    module = db.relationship("Module", back_populates="resources")
    resource = db.relationship("Resource", back_populates="modules")

    def __repr__(self):
        return f"<ModuleResource(id={self.id})>"


class UserAchievement(db.Model, SerializerMixin):
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="achievements")
    achievement = db.relationship("Achievement", back_populates="users")

    def __repr__(self):
        return f"<UserAchievement(id={self.id})>"


class UserLearningPath(db.Model, SerializerMixin):
    __tablename__ = 'user_learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))
    progress_percentage = db.Column(db.Integer)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship("User", back_populates="enrolled_paths")
    learning_path = db.relationship("LearningPath", back_populates="enrolled_users")

    def __repr__(self):
        return f"<UserLearningPath(id={self.id})>"


class UserChallenge(db.Model, SerializerMixin):
    __tablename__ = 'user_challenges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship("User", back_populates="challenges")
    challenge = db.relationship("Challenge", back_populates="users")

    def __repr__(self):
        return f"<UserChallenge(id={self.id})>"


class QuizContent(db.Model, SerializerMixin):
    __tablename__ = 'quiz_content'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'))
    type = db.Column(db.String, nullable=False)  # "quiz", "question", or "option"
    content_text = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer)
    is_correct = db.Column(db.Boolean)

    # Relationships
    module = db.relationship("Module", back_populates="quiz_content")
    parent = db.relationship("QuizContent", remote_side=[id], back_populates="children")
    children = db.relationship("QuizContent", back_populates="parent")

    def __repr__(self):
        return f"<QuizContent(id={self.id})>"


class QuizSubmission(db.Model, SerializerMixin):
    __tablename__ = 'quiz_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'))
    score = db.Column(db.Integer)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="quiz_submissions")
    quiz = db.relationship("QuizContent")

    def __repr__(self):
        return f"<QuizSubmission(id={self.id})>"
