import os
from django.core.management.base import BaseCommand
from csgoogleanalytics.utils import create_analytics
from django.conf import settings


class Command(BaseCommand):
    args = "Updates Analytics most viewed data"
    help = "Updates Analytics most viewed data"

    def handle(self, *args, **options):
        create_analytics()
