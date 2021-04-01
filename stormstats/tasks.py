from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.utils.log import get_task_logger
from scripts import db
from stormstats.models import Game

logger = get_task_logger(__name__)

@shared_task(name = "update_db")
def update_db():
    db.games_update(20202021)
    logger.info("Updated Games")
    db.players_update()
    logger.info("Updated Players")
    db.goalie_overall_stats_update(20202021)
    db.skater_overall_stats_update(20202021)
    logger.info("Updated Overall Stats")
    for x in Game.objects.values():
        if (x["played"] == True):
            db.game_stats_update(x["game_id"])
    logger.info("Updated Game Stats")