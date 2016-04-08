import os
import random

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User

from django.db import connections
from django.core.management.color import no_style

import sqlite3


class Profile(models.Model):
    class Meta:
        db_table = 'profile'

    user = models.ForeignKey(User)  # Changed
    token = models.CharField(max_length=255)
    userFavorites = models.CommaSeparatedIntegerField(blank=True, default='', max_length=1000)
    activation_key = models.CharField(max_length=50)
    folder_path = models.FilePathField(blank=True, default='')

    def __str__(self):
        return self.user.username


class Advertisement(models.Model):
    class Meta:
        ordering = ['category', 'title']
        db_table = 'advertisement'

    profile = models.ForeignKey('Profile')
    category = models.ForeignKey('Category')
    city = models.ForeignKey('City')
    title = models.CharField(max_length=255)
    description = models.TextField()
    condition = models.BooleanField(help_text='Check - New thing, None - Used thing')  # New - True, if used one - False
    price = models.IntegerField(validators=[MinValueValidator(limit_value=0.01)])
    phone = models.CharField(max_length=100)
    image_titles = models.CharField(max_length=255, default='')  # '1407107f.png,da7809b6.jpg ... to 5 '

    # Additional Fields
    housing = models.ForeignKey('Housing', blank=True, null=True)
    transport = models.ForeignKey('Transport', blank=True, null=True)
    clothes = models.ForeignKey('Clothes', blank=True, null=True)
    kids_things = models.ForeignKey('KidsThings', blank=True, null=True)
    recreation = models.ForeignKey('Recreation', blank=True, null=True)

    def __str__(self):
        return self.title


class Housing(models.Model):
    """
        Description for <House and garden, apartment, Rent>
    """
    class Meta:
        ordering = ['area']
        db_table = 'housing'
        verbose_name_plural = 'Housing'

    communications = models.TextField()
    area = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(limit_value=0.01)])

    def __str__(self):
        return '%s - %s m2' % (self.communications, str(self.area))


class Transport(models.Model):
    """
        Description for <Cars, motorcycles, bicycles>
    """
    class Meta:
        ordering = ['year']
        db_table = 'transport'
        verbose_name_plural = 'Transport'

    year = models.PositiveSmallIntegerField()
    motor_power = models.PositiveSmallIntegerField()
    color = models.CharField(max_length=100)

    def __str__(self):
        return '%s year %s cm3 %s' % (str(self.year), str(self.motor_power), self.color)


class Clothes(models.Model):
    """
        Description for <Adult Clothes>
    """
    class Meta:
        db_table = 'clothes'
        verbose_name_plural = 'Clothes'

    sex = models.BooleanField(help_text='Check - for Male , None - for Female')  # 1 - for male , 0 - for female

    def __str__(self):
        if self.sex:
            sex_line = 'Male'
        else:
            sex_line = 'Female'
        return sex_line


class KidsThings(models.Model):
    """
        Description for <All for children>
    """
    class Meta:
        ordering = ['age']
        db_table = 'kids_things'
        verbose_name_plural = 'Kids Things'

    sex = models.BooleanField(help_text='Check - for boy , None - for girl')  # 1 - for boy , 0 - for girl
    age = models.PositiveSmallIntegerField()  # age of kid

    def __str__(self):
        if self.sex:
            sex_line = 'Boy'
        else:
            sex_line = 'Girl'
        return '%s - %s year' % (sex_line, str(self.age))


class Recreation(models.Model):
    """
        Description for <Recreation, Tourism>
    """
    class Meta:
        ordering = ['name']
        db_table = 'recreation'
        verbose_name_plural = 'Recreation'

    name = models.CharField(max_length=200)  # name of vacation spot

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        db_table = 'category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=255, unique=True)
    # icon = models.FilePathField()  # NEW, change size in px
    notification_counter = models.IntegerField(default=0)  # counter for current category. Use in push-notifications
    subscribers_table = models.CharField(max_length=255, blank=True, null=True)  # запретить редактирование.

    @staticmethod
    def create_table(database='db.sqlite3', name=''):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        table_name = str("subscribers_" + name)

        try:
            cursor.execute("CREATE TABLE %s ("
                           "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                           "profile_id INTEGER NOT NULL UNIQUE "
                           ");" % table_name)

            connection.commit()
        except sqlite3.Error as e:
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

        return table_name

    @staticmethod
    def drop_table(database='db.sqlite3', table_name=''):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            cursor.execute("DROP TABLE %s;" % table_name)
            connection.commit()
        except sqlite3.Error as e:
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    @staticmethod
    def insert_row(database='db.sqlite3', table_name="", profile_list=list()):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            row_id = cursor.lastrowid
            for profile_id in profile_list:
                cursor.execute("INSERT INTO %s (id, profile_id) VALUES(?, ?);" % table_name, (row_id, profile_id))
                connection.commit()
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    @staticmethod
    def delete_row(database='db.sqlite3', table_name="", profile_list=list()):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            for profile_id in profile_list:
                cursor.execute("DELETE FROM %s WHERE profile_id = ?;" % table_name, (profile_id,))
                connection.commit()
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.subscribers_table = self.create_table(database='db.sqlite3', name=str(self.name))
        super(Category, self).save()

    def delete(self, using=None, keep_parents=False):
        self.drop_table(database='db.sqlite3', table_name=self.subscribers_table)
        super(Category, self).delete()

    def __str__(self):
        return self.name


class City(models.Model):
    class Meta:
        db_table = 'city'
        verbose_name_plural = 'Cities'

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

"""
class Subscribers(models.Model):
    class Meta:
        db_table = 'subscribers'
        abstract = True

    # maybe add id = AutoField
    profile_id = models.IntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return 'subscribers'
"""
