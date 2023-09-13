from django.db import migrations

SOURCE_BACKEND_MAPPING = {
    'mayan.apps.sources.source_backends.email_backends.SourceBackendIMAPEmail': 'mayan.apps.source_emails.source_backends.email_backends.SourceBackendIMAPEmail',
    'mayan.apps.sources.source_backends.email_backends.SourceBackendPOP3Email': 'mayan.apps.source_emails.source_backends.email_backends.SourceBackendPOP3Email',
    'mayan.apps.sources.source_backends.sane_scanner_backends.SourceBackendSANEScanner': 'mayan.apps.source_sane_scanners.source_backends.sane_scanner_backends.SourceBackendSANEScanner',
    'mayan.apps.sources.source_backends.staging_folder_backends.SourceBackendStagingFolder': 'mayan.apps.source_staging_folders.source_backends.staging_folder_backends.SourceBackendStagingFolder',
    'mayan.apps.sources.source_backends.watch_folder_backends.SourceBackendWatchFolder': 'mayan.apps.source_watch_folders.source_backends.watch_folder_backends.SourceBackendWatchFolder',
    'mayan.apps.sources.source_backends.web_form_backends.SourceBackendWebForm': 'mayan.apps.source_web_forms.source_backends.web_form_backends.SourceBackendWebForm'
}


def code_source_backend_path_update(apps, schema_editor):
    Source = apps.get_model(app_label='sources', model_name='Source')

    for key, value in SOURCE_BACKEND_MAPPING.items():
        queryset = Source.objects.using(alias=schema_editor.connection.alias).filter(backend_path=key)
        queryset.update(backend_path=value)


def reverse_code_source_backend_path_update(apps, schema_editor):
    Source = apps.get_model(app_label='sources', model_name='Source')

    for key, value in SOURCE_BACKEND_MAPPING.items():
        queryset = Source.objects.using(alias=schema_editor.connection.alias).filter(backend_path=value)
        queryset.update(backend_path=key)


class Migration(migrations.Migration):
    dependencies = [
        ('sources', '0028_auto_20210905_0558')
    ]

    operations = [
        migrations.RunPython(
            code=code_source_backend_path_update,
            reverse_code=reverse_code_source_backend_path_update
        )
    ]
