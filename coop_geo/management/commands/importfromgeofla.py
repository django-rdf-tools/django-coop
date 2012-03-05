#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from geodjangofla.models import Commune, Departement, Canton
from coop_geo import models

class Command(BaseCommand):
    args = '<numero_departements>'
    help = 'Import des donnees depuis l\'application geodjangofla en base de '\
           'donnees'
    option_list = BaseCommand.option_list + (
        make_option('-u', '--update',
            action="store_true",
            dest="update", default=False,
            help="force la mise a jour"),
        )

    def handle(self, *args, **options):
        update = 'update' in options and options['update']

        if not args:
            raise CommandError("Veuillez entrer au moins un numero de "\
                               "departement")
        for dpt in args:
            try:
                assert len(dpt) < 3
            except AssertionError:
                raise CommandError("Le numero de departement %s n'est pas "\
                                   "valide." % dpt)
            dpt = len(dpt) == 1 and "0" + dpt or dpt
            self.stdout.write('Departement %s\n' % dpt)
            departement = Departement.objects.filter(code_dept=dpt)
            if not departement.count():
                raise CommandError("Le numero de departement %s n'est présent "\
                                   "dans la base geofla." % dpt)
            departement = departement.all()[0]
            ref_dpt = models.Area.objects.filter(reference=dpt,
                                                 area_type='DP')
            def_loc = {'city':departement.nom_chf,
                       'label':u"Préfecture",
                       'point':departement.chf_lieu}
            if not ref_dpt.count():
                loc = models.Location.objects.create(**def_loc)
                ref_dpt = models.Area.objects.create(**{
                                'label':departement.nom_dept,
                                'reference':dpt,
                                'polygon':departement.limite,
                                'default_location':loc,
                                'area_type':'DP'})
            else:
                ref_dpt = ref_dpt.all()[0]
                if update:
                    ref_dpt.polygon = departement.limite
                    ref_dpt.save()
                    for k in def_loc:
                        setattr(ref_dpt.default_location, k, def_loc[k])
                    ref_dpt.default_location.save()
                    
            # for idx,canton in enumerate(Canton.objects.filter(code_dept=dpt)):
            #     code_canton = str(canton.code_dept + canton.code_cant)
            #     ref = models.Area.objects.filter(reference=code_canton,
            #                                                 area_type='CT')
            #     def_loc = {'city':canton.nom_chf,
            #                'label':u"Chef-lieu de canton",
            #                'point':canton.chf_lieu}
            #     if ref.count():
            #         if not update:
            #             continue
            #         ref = ref.all()[0]
            #         ref.polygon = canton.limite
            #         ref.save()
            #         for k in def_loc:
            #             setattr(ref.default_location, k, def_loc[k])
            #         ref.default_location.save()
            #     else:
            #         loc = models.Location.objects.create(**def_loc)
            #         ref = models.Area.objects.create(**{
            #                           'label':str('CANTON DE '+canton.nom_chf),
            #                           'reference':code_canton,
            #                           'polygon':canton.limite,
            #                           'default_location':loc,
            #                           'area_type':'CT'})            
                                               
            for idx,commune in enumerate(Commune.objects.filter(
                                          insee_com__startswith=dpt)):
                ref = models.Area.objects.filter(reference=commune.insee_com,
                                                 area_type='TW')
                def_loc = {'city':commune.nom_comm,
                           'label':u"Mairie",
                           'point':commune.chf_lieu}
                if ref.count():
                    if not update:
                        continue
                    ref = ref.all()[0]
                    ref.polygon = commune.limite
                    ref.save()
                    for k in def_loc:
                        setattr(ref.default_location, k, def_loc[k])
                    ref.default_location.save()
                else:
                    loc = models.Location.objects.create(**def_loc)
                    ref = models.Area.objects.create(**{
                                                  'label':commune.nom_comm,
                                                  'reference':commune.insee_com,
                                                  'polygon':commune.limite,
                                                  'default_location':loc,
                                                  'area_type':'TW'})
                #ref_canton = Canton.objects.get(id_geofla=commune.canton_id)
                #ref_canton.add_child(ref, 'CT')
                ref_dpt.add_child(ref, 'DP')
                self.stdout.write('\t- Commune : %d\r' % idx)
            self.stdout.write('\n\n')
        self.stdout.write('Import fini\n')
