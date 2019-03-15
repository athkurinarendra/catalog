from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Guns_Setup import *

engine = create_engine('sqlite:///guns.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete GunsCompanyName if exisitng.
session.query(GunsmodelsName).delete()
# Delete GunName if exisitng.
session.query(GunsName).delete()
# Delete User if exisitng.
session.query(GmailUser).delete()

# Create sample users data
User1 = GmailUser(name="A.L.NARENDRA KUMAR",
                 email="a.l.narendra1229@gmail.com",
                 )
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample Guns companys
models1 = GunsmodelsName(name="Military",
                     user_id=1)
session.add(models1)
session.commit()

models2 = GunsmodelsName(name="Machine guns",
                     user_id=1)
session.add(models2)
session.commit

models3 = GunsmodelsName(name="Hunting",
                     user_id=1)
session.add(models3)
session.commit()

models4 = GunsmodelsName(name="Handguns",
                     user_id=1)
session.add(models4)
session.commit()

models5 = GunsmodelsName(name="Rescue equipment",
                     user_id=1)
session.add(models5)
session.commit()

models6 = GunsmodelsName(name="Training and entertainment",
                     user_id=1)
session.add(models6)
session.commit()

# Populare a guns with models for testing
# Using different users for guns names year also
Guns1 = GunsName(gunsname="Long gun",
                       launchyear="2007",
                       killrating="9.2",
                       price="1,00,000/-",
                       gunstype="which can be fired by sinle hand",
                       date=datetime.datetime.now(),
                       gunsmodelsnameid=1,
                       gmailuser_id=1)
session.add(Guns1)
session.commit()

Guns2 = GunsName(gunsname="Squad Automatic Weapon",
                       launchyear="2010",
                       killrating="10",
                       price="2,89,000/-",
                       gunstype="military-forces",
                       date=datetime.datetime.now(),
                       gunsmodelsnameid=2,
                       gmailuser_id=1)
session.add(Guns2)
session.commit()

Guns3 = GunsName(gunsname="Shotgun",
                       launchyear="2009",
                       killrating="8.9",
                       price="2,500,00/-",
                       gunstype="first-person shooter",
                       date=datetime.datetime.now(),
                       gunsmodelsnameid=3,
                       gmailuser_id=1)
session.add(Guns3)
session.commit()

Guns4 = GunsName(gunsname="Service pistol",
                       launchyear="2012",
                       killrating="9",
                       price="9,50,000/-",
                       gunstype="protecting ourself",
                       date=datetime.datetime.now(),
                       gunsmodelsnameid=4,
                       gmailuser_id=1)
session.add(Guns4)
session.commit()

Guns5 = GunsName(gunsname="Flare gun ",
                       launchyear="2001",
                       killrating="9.5",
                       price="1,065,00/-",
                       gunstype="action role-play",
                       date=datetime.datetime.now(),
                       gunsmodelsnameid=5,
                       gmailuser_id=1)
session.add(Guns5)
session.commit()

Guns6 = GunsName(gunsname="Water gun",
                       launchyear="2012",
                       killrating="8.5",
                       price="7,30,000/-",
                       gunstype=" person protect in water",
                       date=datetime.datetime.now(),
                       gunsmodelsnameid=6,
                       gmailuser_id=1)
session.add(Guns6)
session.commit()

print("Your guns database has been inserted!")
