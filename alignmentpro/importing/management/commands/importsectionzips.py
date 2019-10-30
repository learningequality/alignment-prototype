import os
import re
import shutil
import sys

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand


from alignmentapp.models import CurriculumDocument, DocumentSection



def is_chunks_dir(dirpath):
    filenames = os.listdir(dirpath)
    return any(filename.endswith('_combined.txt') for filename in filenames)


def get_chunksdir_section_name(dirpath):
    filenames = os.listdir(dirpath)
    candidates = [filename for filename in filenames if filename.endswith('_combined.txt')]
    assert len(candidates) == 1, 'failed to find _combined.txt in chunkdir ' + dirpath
    return candidates[0].replace('_combined.txt', '')


def import_chunksdir(folderpath, parent_section):
    section_name = get_chunksdir_section_name(folderpath)
    if parent_section.get_children().filter(name=section_name).exists():
        section = parent_section.get_children().get(name=section_name)
    else:
        print(' '*3*parent_section.depth, 'creating new chunksdir', section_name)
        section = parent_section.add_child(document=parent_section.document, name=section_name)    
        zipbasename = os.path.join(settings.UPLOADS_ROOT, section_name)
        zippath = zipbasename + '.zip'
        shutil.make_archive(zipbasename, 'zip', folderpath)
        zip_djfile = File(open(zippath,'rb'))
        section.section_zip = zip_djfile
        section.save()


def import_folder(folderpath, parent_section):
    """
    Imports chunkedscans folder by creating a DocumentSection from folderpath.
    For each child:
      - if child is an inner folder calles itself recusively
      - if non-empty topic folder, calls import_chunksdir to createe DocumentSection with a section_zip
    """
    # print('in import_folder with folderpath= ', folderpath, 'parent_section=', parent_section)
    dirname = os.path.split(folderpath)[-1]
    _sort_order, section_name = dirname.split('_', maxsplit=1)
    
    if parent_section.get_children().filter(name=section_name).exists():
        section = parent_section.get_children().get(name=section_name)
    else:
        print(' '*3*parent_section.depth, 'creating new section', section_name)
        section = parent_section.add_child(document=parent_section.document, name=section_name)

    childdirsnames = [f for f in os.listdir(folderpath) if os.path.isdir(os.path.join(folderpath, f))]

    # import chunksdir children 
    kicd_topic_pat = re.compile('(\d*)\.0\.0')    
    chunks_childdirs = []
    for childdirsname in childdirsnames:
        childdirpath = os.path.join(folderpath, childdirsname)
        m = kicd_topic_pat.search(childdirsname)
        if m:
            sort_order = int(m.group(1))
            chunks_childdirs.append( (sort_order, childdirpath))
    for _sort_order, childdirpath in sorted(chunks_childdirs, key=lambda t: t[0]):
        if is_chunks_dir(childdirpath):
            import_chunksdir(childdirpath, section)
        else:
            pass
            # print('skipping empty childdirpath', childdirpath)

    # recurse in subdirs with underscores
    for childdirname in sorted([f for f in childdirsnames if '_' in f]):
        childfolderpath = os.path.join(folderpath, childdirname)
        import_folder(childfolderpath, section)



class Command(BaseCommand):
    """
    Import the DocumentSection tree structure and topic chunks.
    """

    def add_arguments(self, parser):
        parser.add_argument("--sourcedir", type=str, required=True, help='Directory containing document (subdir of chunkedscans)')

    def handle(self, *args, **options):
        print("Starting data export...")
        print("options=", options)

        sourcedir = options['sourcedir']
        if not os.path.exists(sourcedir):
            print('source directory', sourcedir, 'not found')
            sys.exit(-1)

        document_source_dir = os.path.basename(sourcedir)
        document_source_id, document_title = document_source_dir.split('_', maxsplit=1)
        if CurriculumDocument.objects.filter(source_id=document_source_id).exists():
            document = CurriculumDocument.objects.get(source_id=document_source_id)
            print('Document alrady exists', document)
        else:
            print('Creating document', document_source_id, document_title)
            document = CurriculumDocument.objects.create(
                source_id=document_source_id,
                title=document_title,
                country='Kenya',
                digitization_method='semiautomated_scan',
            )

        if DocumentSection.objects.filter(document=document, name=document_title, depth=1).exists():
            root_section = DocumentSection.objects.get(document=document, name=document_title, depth=1)
        else:
            root_section = DocumentSection.add_root(document=document, name=document_title)
        
        documentfolderpath = sourcedir
        childdirsnames = [f for f in os.listdir(documentfolderpath) if os.path.isdir(os.path.join(documentfolderpath, f))]
        for childdirname in sorted([f for f in childdirsnames if '_' in f]):
            folderpath = os.path.join(documentfolderpath, childdirname)
            import_folder(folderpath, root_section)

