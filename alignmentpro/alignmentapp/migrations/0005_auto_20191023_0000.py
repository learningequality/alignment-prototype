# Generated by Django 2.2.6 on 2019-10-23 00:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alignmentapp', '0004_auto_20191013_2141'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=100)),
                ('section_zip', models.FileField(blank=True, null=True, upload_to='')),
                ('num_chunks', models.IntegerField()),
                ('text', models.TextField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chunks', to='alignmentapp.CurriculumDocument')),
            ],
        ),
        migrations.DeleteModel(
            name='MachineLearningModel',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='background',
            field=models.CharField(choices=[('instructional_designer', 'Instructional Designer'), ('curriculum', 'Curriculum Alignment Expert'), ('content_expert', 'OER Expert'), ('teacher', 'Teacher/Coach'), ('designer', 'Designer or Frontend Developer'), ('developer', 'Technologist and/or Developer'), ('data_science', 'Machine Learning and Data Science'), ('metadata', 'Metadata'), ('other', 'Other')], help_text='What is your background experience?', max_length=50),
        ),
        migrations.AddConstraint(
            model_name='documentsection',
            constraint=models.UniqueConstraint(condition=models.Q(depth=1), fields=('document', 'depth'), name='document_section_single_root'),
        ),
    ]
