Common Standards Project Data Importer
======================================

Pipeline

  - Use this code base https://github.com/commonstandardsproject/standards-importer 
    to load the Common Standards data into a local Postgres DB called `standards`
  - Use Django ORM models to extract

```python
from commonstandardsproject.models import Jurisdictions, Standards

ccssj = Jurisdictions.objects.filter(title__icontains='common core')[0]
for r in ccssj.get_roots().order_by('subject'):
    print(r.id, r.subject, r.title)

# 157732 Arte Lenguaje en Español Kindergarten
# 157494 Arte Lenguaje en Español Primer Grado
# 157623 Arte Lenguaje en Español Segundo Grado
# 155027 Common Core English/Language Arts Grade 2
# 157158 Common Core English/Language Arts Grade 8
# 155575 Common Core English/Language Arts Grades 11, 12
# 155412 Common Core English/Language Arts Grade 4
# 156951 Common Core English/Language Arts Grade 6
# 155249 Common Core English/Language Arts Grade 1
# 156181 Common Core English/Language Arts Grade 3
# 156747 Common Core English/Language Arts Grade 7
# 156027 Common Core English/Language Arts Grade K
# 154699 Common Core English/Language Arts Grades 9, 10
# 156478 Common Core English/Language Arts Grade 5
# 154300 Common Core Mathematics Grade 8
# 157364 Common Core Mathematics High School — Statistics and Probability
# 156688 Common Core Mathematics High School — Algebra
# 156639 Common Core Mathematics Grade K
# 156348 Common Core Mathematics Grade 7
# 155961 Common Core Mathematics Grade 5
# 156415 Common Core Mathematics Grade 3
# 155892 Common Core Mathematics High School — Functions
# 155776 Common Core Mathematics Grade 2
# 155828 Common Core Mathematics Grade 4
# 154902 Common Core Mathematics High School — Geometry
# 155177 Common Core Mathematics Grade 6
# 154416 Common Core Mathematics Grades 9, 10, 11, 12
# 154361 Common Core Mathematics High School — Number and Quantity
# 154978 Common Core Mathematics Grade 1
# 157454 English Language Arts - History/Social Studies 6-8
# 157423 English Language Arts - Science and Technical Subjects Grade 9-10
# 157438 English Language Arts - Science and Technical Subjects 6-8
# 157469 English Language Arts - Writing (History/Social Studies, Science, & Technical Subjects) 6-8


ngssj = Jurisdictions.objects.filter(title__icontains='next generation')[0]
for r in ngssj.get_roots().order_by('subject'):
    print(r.id, r.subject, r.title)

# 507090 Crosscutting Concepts Middle School
# 507222 Life Science Middle School
# 506992 Physical Science Middle School
# 505606 Science Grade 2
# 507082 Science Crosscutting Concepts
# 505934 Science Grades 9, 10, 11, 12
# 505846 Science Grade 1
# 505708 Science Grade 4
# 506865 Science Grade 5
# 506764 Science Grade K
# 506630 Science Grade 3
# 507054 Science Life Sciences
# 507019 Science
# 506303 Science Grades 6, 7, 8
# 507073 Science Practices
# 507105 Science Practices Middle school science
# 507165 Science and Engineering Practices High School Science

```