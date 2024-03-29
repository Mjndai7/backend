# Generated by Django 4.2.7 on 2024-02-07 12:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=255)),
                ('job_description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document', models.FileField(blank=True, null=True, upload_to='attachments')),
                ('status', models.CharField(choices=[('active', 'active'), ('working', 'working'), ('ended', 'ended')], default='active', max_length=12)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultant', to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'job',
                'verbose_name_plural': 'jobs',
                'unique_together': {('client', 'date_created')},
            },
        ),
        migrations.CreateModel(
            name='JobProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proposal', models.TextField()),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_proposal', to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_proposal', to='jobs.job')),
            ],
            options={
                'unique_together': {('job', 'consultant')},
            },
        ),
    ]
