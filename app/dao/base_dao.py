from app.db import db

class BaseDAO:
    model = None

    @classmethod
    def get_by_id(cls, entity_id):
        return db.session.get(cls.model, entity_id)

    @classmethod
    def get_all(cls):
        return cls.model.query.all()

    @classmethod
    def save(cls, entity):
        db.session.add(entity)
        db.session.commit()
        return entity

    @classmethod
    def delete(cls, entity):
        db.session.delete(entity)
        db.session.commit()
