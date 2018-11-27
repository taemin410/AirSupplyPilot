# Generated by Django 2.1.2 on 2018-11-16 11:29

import ASP_app.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('altitude', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Dispatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('droneID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=512)),
                ('shippingWeight', models.FloatField()),
                ('picture', models.ImageField(blank=True, null=True, upload_to=ASP_app.models.get_image_path)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], max_length=128)),
                ('status', models.CharField(blank=True, choices=[('Queued for Processing', 'Queued for Processing'), ('Processing by Warehouse', 'Processing by Warehouse'), ('Queued for Dispatch', 'Queued for Dispatch'), ('Dispatched', 'Dispatched'), ('Delivered', 'Delivered')], max_length=256)),
                ('orderTime', models.DateTimeField(auto_now_add=True)),
                ('dispatchTime', models.DateTimeField(blank=True, null=True)),
                ('deliveryTime', models.DateTimeField(blank=True, null=True)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ASP_app.Clinic')),
            ],
        ),
        migrations.CreateModel(
            name='OrderedItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('medicineID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ASP_app.Medicine')),
                ('orderID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ASP_app.Order')),
            ],
        ),
        migrations.CreateModel(
            name='ProcessedDispatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dispatchID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ASP_app.Dispatch')),
            ],
        ),
        migrations.CreateModel(
            name='ShippingLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contents', models.CharField(max_length=512)),
                ('finalDestination', models.CharField(max_length=256)),
                ('orderID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ASP_app.Order')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('username', models.CharField(blank=True, max_length=30, unique=True, verbose_name='username')),
                ('firstname', models.CharField(blank=True, max_length=20, verbose_name='firstname')),
                ('lastname', models.CharField(blank=True, max_length=20, verbose_name='lastname')),
                ('password', models.CharField(blank=True, max_length=30, verbose_name='password')),
            ],
        ),
        migrations.AddField(
            model_name='processeddispatch',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ASP_app.User'),
        ),
        migrations.AddField(
            model_name='dispatch',
            name='orderID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ASP_app.Order'),
        ),
    ]
