import os
import random

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User

from django.db import connections
from django.core.management.color import no_style

from bazzzar.settings import DATABASE_NAME

import sqlite3
import datetime


class Profile(models.Model):
    class Meta:
        db_table = 'profile'

    user = models.ForeignKey(User)  # Changed
    token = models.CharField(max_length=255)
    userFavorites = models.CommaSeparatedIntegerField(blank=True, default='', max_length=1000)
    userSubscriptions = models.CommaSeparatedIntegerField(blank=True, default='', max_length=1000)
    # activation_key = models.CharField(max_length=50)
    folder_path = models.FilePathField(blank=True, default='')
    android_tokens = models.CharField(max_length=10000, default='')
    ios_tokens = models.CharField(max_length=10000, default='')
    datatime_favorites = models.DateTimeField(blank=True, null=True)
    datatime_subscriptions = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    class Meta:
        db_table = 'category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=255, unique=True)
    # icon = models.FilePathField()  # NEW, change size in px
    notification_counter = models.IntegerField(default=0)  # counter for current category. Use in push-notifications
    subscribers_table = models.CharField(max_length=255, blank=True, null=True)  # запретить редактирование.
    extrafield_values_table = models.CharField(max_length=255, blank=True, null=True)

    @staticmethod
    def create_table_subscribers(database=DATABASE_NAME, name=''):
        """
        Create subscribers table for current category
        """
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

    def insert_row_subscriber(self, database=DATABASE_NAME, profile_list=list()):
        """
        Insert profile id to  subscribers table from current category
        """
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            row_id = cursor.lastrowid
            for profile_id in profile_list:
                cursor.execute("INSERT INTO %s (id, profile_id) VALUES(?, ?);" % self.subscribers_table,
                               (row_id, profile_id,))
                connection.commit()

        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    def select_all_subscribers(self, database=DATABASE_NAME):
        """
        Select all subscribers(profile ids) from table related with current category
        """
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        id_list = list()

        try:
            for row in cursor.execute('SELECT profile_id FROM %s ORDER BY profile_id' % self.subscribers_table):
                id_list += list(row)    # convert tuple to list

        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

        return id_list

    def delete_row_subscriber(self, database=DATABASE_NAME, profile_list=list()):
        """
        Delete subscriber(profile id) from table
        """
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            for profile_id in profile_list:
                cursor.execute("DELETE FROM %s WHERE profile_id = ?;" % self.subscribers_table, (profile_id,))
                connection.commit()
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    @staticmethod
    def create_table_extrafields(database=DATABASE_NAME, name=''):
        """
        Create table for extra fields values for current category
        """
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        table_name = str("extrafields_" + name)

        try:
            cursor.execute("CREATE TABLE %s ("
                           "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                           "extrafield_id INTEGER NOT NULL, "
                           "advertisement_id INTEGER NOT NULL, "
                           "string_value CHAR "
                           ");" % table_name)

            connection.commit()
        except sqlite3.Error as e:
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

        return table_name

    def insert_row_extrafield(self, database=DATABASE_NAME, extrafield_id=int(),
                              advertisement_id=int(), string_value=''):

        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            row_id = cursor.lastrowid
            cursor.execute("INSERT INTO %s (id, extrafield_id, advertisement_id, string_value) VALUES(?, ?, ?, ?);"
                           % self.extrafield_values_table, (row_id, extrafield_id, advertisement_id, string_value,))
            connection.commit()

        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    def update_row_extrafield(self, database=DATABASE_NAME, string_value=str(),
                              extrafield_id=int(), advertisement_id=int()):

        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            cursor.execute("UPDATE %s SET string_value=? WHERE extrafiled_id=?, advertisement_id=?;"
                           % self.extrafield_values_table, (string_value, extrafield_id, advertisement_id,))
            connection.commit()

        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    def select_row_extrafield(self, database=DATABASE_NAME, string_value=str(),
                              extrafield_id=int(), advertisement_id=int()):
        """
        Search specific row by all parameters, return True or False
        """
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        select_or_not = False
        try:
            cursor.execute('SELECT * FROM %s WHERE extrafield_id=?, advertisement_id=?, string_value=?'
                           % self.extrafield_values_table, (extrafield_id, advertisement_id, string_value,))
            select_or_not = True
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

        return select_or_not

    def select_all_extrafields(self, database=DATABASE_NAME, advertisement_id=int()):
        """
        Select all extra fields related to this advertisement by id
        """
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        fields_list = list()

        try:
            for row in cursor.execute('SELECT extrafield_id, string_value FROM %s '
                                      'WHERE advertisement_id=? ORDER BY extrafield_id'
                                      % self.extrafield_values_table, (advertisement_id,)):
                param_dict = dict()
                param_dict['id'] = row[0]    # add to dict
                param_dict['value'] = row[1]
                fields_list.append(param_dict)

        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

        return fields_list

    def delete_rows_extrafield(self, database=DATABASE_NAME, advertisement_id=int()):
        """
        Delete related adv extra fields from db table
        """
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM %s WHERE advertisement_id = ?;"
                           % self.extrafield_values_table, (advertisement_id,))
            connection.commit()
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    @staticmethod
    def drop_table(database=DATABASE_NAME, table_name=''):
        """
        Drop table with table_name from system
        """
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        try:
            cursor.execute("DROP TABLE %s;" % table_name)
            connection.commit()
        except sqlite3.Error as e:
            print("Error %s:" % e.args[0])

        finally:
            connection.close()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.subscribers_table is None:
            self.subscribers_table = self.create_table_subscribers(name=str(self.name))
        if self.extrafield_values_table is None:
            self.extrafield_values_table = self.create_table_extrafield(name=str(self.name))

        datatime_category_table = DatatimeTable.objects.get(name=Category._meta.db_table)
        datatime_category_table.datatime = datetime.datetime.now()
        datatime_category_table.save()

        super(Category, self).save()

    def delete(self, using=None, keep_parents=False):
        self.drop_table(table_name=self.subscribers_table)  # drop subscribers table
        self.drop_table(table_name=self.extrafield_values_table)    # drop extra fields table for category

        datatime_category_table = DatatimeTable.objects.get(name=Category._meta.db_table)
        datatime_category_table.datatime = datetime.datetime.now()
        datatime_category_table.save()

        super(Category, self).delete()

    def __str__(self):
        return self.name


class ExtraFieldDescription(models.Model):
    """
        Extra field configuration table
    """
    class Meta:
        ordering = ['category__name', 'name']
        db_table = 'extrafield_description'

    DATA_TYPES = (
        ('int', 'Integer'),
        ('str', 'String'),
        ('bool', 'Boolean'),
    )

    category = models.ForeignKey(Category)
    name = models.CharField(max_length=255)
    min_int = models.IntegerField(blank=True, null=True)
    max_int = models.IntegerField(blank=True, null=True)
    string_set = models.TextField(blank=True, null=True)
    boolean = models.NullBooleanField()
    data_type = models.CharField(max_length=100, choices=DATA_TYPES, blank=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        datatime_extrafield_table = DatatimeTable.objects.get(name=ExtraFieldDescription._meta.db_table)
        datatime_extrafield_table.datatime = datetime.datetime.now()
        datatime_extrafield_table.save()

        super(ExtraFieldDescription, self).save()

    def delete(self, using=None, keep_parents=False):
        datatime_extrafield_table = DatatimeTable.objects.get(name=ExtraFieldDescription._meta.db_table)
        datatime_extrafield_table.datatime = datetime.datetime.now()
        datatime_extrafield_table.save()

        super(ExtraFieldDescription, self).delete()

    def __str__(self):
        return '%s - %s' % (self.category.name, self.name)


class City(models.Model):
    class Meta:
        db_table = 'city'
        verbose_name_plural = 'Cities'

    name = models.CharField(max_length=100)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        datatime_city_table = DatatimeTable.objects.get(name=City._meta.db_table)
        datatime_city_table.datatime = datetime.datetime.now()
        datatime_city_table.save()

        super(City, self).save()

    def delete(self, using=None, keep_parents=False):
        datatime_city_table = DatatimeTable.objects.get(name=City._meta.db_table)
        datatime_city_table.datatime = datetime.datetime.now()
        datatime_city_table.save()

        super(City, self).delete()

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    class Meta:
        ordering = ['category', 'title']
        db_table = 'advertisement'

    profile = models.ForeignKey(Profile)
    category = models.ForeignKey(Category)
    city = models.ForeignKey(City)

    title = models.CharField(max_length=255)
    description = models.TextField()
    condition = models.BooleanField(help_text='Check - New thing, None - Used thing')  # New - True, if used one - False
    price = models.IntegerField(validators=[MinValueValidator(limit_value=0.01)])
    phone = models.CharField(max_length=100)
    image_titles = models.CharField(max_length=255, default='')  # '1407107f.png,da7809b6.jpg ... to 5 '
    datatime = models.DateTimeField(auto_now_add=True)

    # Additional Fields
    """
    housing = models.ForeignKey('Housing', blank=True, null=True)
    transport = models.ForeignKey('Transport', blank=True, null=True)
    clothes = models.ForeignKey('Clothes', blank=True, null=True)
    kids_things = models.ForeignKey('KidsThings', blank=True, null=True)
    recreation = models.ForeignKey('Recreation', blank=True, null=True)
    """

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        category = Category.objects.get(id=self.category.id)
        category.notification_counter += 1
        category.save()

        super(Advertisement, self).save()

    def __str__(self):
        return self.title


class Commercial(models.Model):  # Create by administration
    class Meta:
        db_table = 'commercials'

    adv_url = models.URLField()
    adv_content = models.URLField()
    adv_title = models.CharField(max_length=100)
    is_shown = models.BooleanField(default=False)

    def __str__(self):
        return self.adv_title


class DatatimeTable(models.Model):
    """
    Class where store last changes(datatime) from tables.
    To add new table to choice list in admin panel, add description to SET_TABLES
    """
    class Meta:
        db_table = 'datatime_table'

    SET_TABLES = (
        (Category._meta.db_table, 'Category Table'),
        (City._meta.verbose_name_plural, 'City Table'),
        (ExtraFieldDescription._meta.db_table, 'Extra Field Description Table'),
    )

    name = models.CharField(max_length=255, choices=SET_TABLES)
    datatime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

"""
class Housing(models.Model):

    class Meta:
        ordering = ['area']
        db_table = 'housing'
        verbose_name_plural = 'Housing'

    communications = models.TextField()
    area = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(limit_value=0.01)])

    def __str__(self):
        return '%s - %s m2' % (self.communications, str(self.area))


class Transport(models.Model):

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

    class Meta:
        ordering = ['name']
        db_table = 'recreation'
        verbose_name_plural = 'Recreation'

    name = models.CharField(max_length=200)  # name of vacation spot

    def __str__(self):
        return self.name
"""
