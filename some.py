from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


class RoleMapping(db.Model):
    __tablename__ = 'role_mapping'
    role_id = db.Column(db.Integer)
    id = db.Column(db.Integer)  #This is the id that corresponds to ids in all other tables record, shmekord, reports, users, etc
    Type = db.Column(db.String) #This one has table names record, shmekord, reports, users, etc
    Role = db.Column(db.String) #Admin,Write,Read

# Custom base model with authorization logic
class CustomBaseModel(db.Model):
    __abstract__ = True

    @classmethod
    def query(cls,action='read'):
        # Query user permissions
		
		role_mappings = RoleMapping.query.filter_by(role_id=user.role_id).all()

        # Define a base query
        query = cls.query
        
        # Apply filtering based on user permissions and table name
        if action == 'read':
            query = query.filter(cls.id.in_(
                db.session.query(RoleMapping.id).\
                join(UserRoles, UserRoles.role_id == RoleMapping.role_id).\
                filter(RoleMapping == 'Read').\
                filter(RoleMapping.Type == cls.__tablename__).\
                filter(UserRoles.user_id == current_user.id).\            # Using class name instead of __table__.name
                distinct()
            ))

        elif action == 'write':
            if 'write' in user_permissions:
                return model_class.query
            else:
                return model_class.query.filter_by(id=None)

        return query
        
    def delete_record(cls, record_id):
        # Add logic for checking if the user is allowed to delete the record
        if current_user.is_authenticated:
            record = cls.query.get(record_id)
            if record:
                db.session.delete(record)
                db.session.commit()
                return True
        return False


# Define Record model (replace with your actual model)
class Record(CustomBaseModel):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String)  # Assuming a field to store the table name

# Define Shmekord model
class Shmekord(CustomBaseModel):
    __tablename__ = 'shmekord'
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String)  # Assuming a field to store the table name

# Define Reports model
class Reports(CustomBaseModel):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String)  # Assuming a field to store the table name
    @classmethod
    def get_reports(cls):
        # Get authorized reports for the user
        return cls.query.all()


# Usage example
if __name__ == "__main__":
    db.create_all()

    # Inserting some data for testing
    # Insert data for users, roles, permissions, and record_permissions tables as needed

    # Authorized query using the authorized_users class method

    authorized_reports = Reports.get_reports()
    deleted_reports = Reports.delete_record(1)
    print(authorized_users)
