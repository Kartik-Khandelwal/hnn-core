"""Model for Pyramidal cell class."""

# Authors: Mainak Jas <mainak.jas@telecom-paristech.fr>
#          Sam Neymotin <samnemo@gmail.com>

import numpy as np

from neuron import h

from .cell import _Cell

from .params import compare_dictionaries
from .params_default import (get_L2Pyr_params_default,
                             get_L5Pyr_params_default)

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted


class Pyr(_Cell):
    """Pyramidal neuron.

    Attributes
    ----------
    name : str
        The name of the cell, 'L5Pyr' or 'L2Pyr'
    dends : dict
        The dendrites. The key is the name of the dendrite
        and the value is an instance of h.Section.
    synapses : dict
        The synapses that the cell can use for connections.
    list_dend : list of str
        List of dendrites.
    sect_loc : dict of list
        Can have keys 'proximal' or 'distal' each containing
        names of section locations that are proximal or distal.
    celltype : str
        The cell type, 'L5Pyr' or 'L2_Pyramidal'
    """

    def __init__(self, gid, soma_props):
        _Cell.__init__(self, gid, soma_props)
        self.create_soma()
        # store cell_name as self variable for later use
        self.name = soma_props['name']
        # preallocate dict to store dends
        self.dends = {}
        self.synapses = dict()
        self.sect_loc = dict()
        # for legacy use with L5Pyr
        self.list_dend = []
        self.celltype = 'Pyramidal'

    def get_sectnames(self):
        """Create dictionary of section names with entries
           to scale section lengths to length along z-axis."""
        seclist = h.SectionList()
        seclist.wholetree(sec=self.soma)
        d = dict((sect.name(), 1.) for sect in seclist)
        for key in d.keys():
            # basal_2 and basal_3 at 45 degree angle to z-axis.
            if 'basal_2' in key:
                d[key] = np.sqrt(2) / 2.
            elif 'basal_3' in key:
                d[key] = np.sqrt(2) / 2.
            # apical_oblique at 90 perpendicular to z-axis
            elif 'apical_oblique' in key:
                d[key] = 0.
            # All basalar dendrites extend along negative z-axis
            if 'basal' in key:
                d[key] = -d[key]
        return d

    def create_dends(self, p_dend_props):
        """Create dendrites."""
        for key in p_dend_props:
            self.dends[key] = h.Section(
                name=self.name + '_' + key)  # create dend
        # apical: 0--4; basal: 5--7
        self.list_dend = [self.dends[key] for key in
                          ['apical_trunk', 'apical_oblique', 'apical_1',
                           'apical_2', 'apical_tuft', 'basal_1', 'basal_2',
                           'basal_3'] if key in self.dends]
        self.sect_loc['proximal'] = ['apicaloblique', 'basal2', 'basal3']
        self.sect_loc['distal'] = ['apicaltuft']

    def set_dend_props(self, p_dend_props):
        """"Iterate over keys in p_dend_props. Create dend for each key."""
        for key in p_dend_props:
            # set dend props
            self.dends[key].L = p_dend_props[key]['L']
            self.dends[key].diam = p_dend_props[key]['diam']
            self.dends[key].Ra = p_dend_props[key]['Ra']
            self.dends[key].cm = p_dend_props[key]['cm']
            # set dend nseg
            if p_dend_props[key]['L'] > 100.:
                self.dends[key].nseg = int(p_dend_props[key]['L'] / 50.)
                # make dend.nseg odd for all sections
                if not self.dends[key].nseg % 2:
                    self.dends[key].nseg += 1

    def get_sections(self):
        ls = [self.soma]
        for key in ['apical_trunk', 'apical_1', 'apical_2', 'apical_tuft',
                    'apical_oblique', 'basal_1', 'basal_2', 'basal_3']:
            if key in self.dends:
                ls.append(self.dends[key])
        return ls

    def get_section_names(self):
        """Get section names."""
        ls = ['soma']
        for key in ['apical_trunk', 'apical_1', 'apical_2', 'apical_tuft',
                    'apical_oblique', 'basal_1', 'basal_2', 'basal_3']:
            if key in self.dends:
                ls.append(key)
        return ls

    def _get_dend_props(self):
        """Returns hardcoded dendritic properties."""
        props = {
            'apical_trunk': {
                'L': self.p_all['%s_apicaltrunk_L' % self.name],
                'diam': self.p_all['%s_apicaltrunk_diam' % self.name],
                'cm': self.p_all['%s_dend_cm' % self.name],
                'Ra': self.p_all['%s_dend_Ra' % self.name],
            },
            'apical_1': {
                'L': self.p_all['%s_apical1_L' % self.name],
                'diam': self.p_all['%s_apical1_diam' % self.name],
                'cm': self.p_all['%s_dend_cm' % self.name],
                'Ra': self.p_all['%s_dend_Ra' % self.name],
            },
            'apical_tuft': {
                'L': self.p_all['%s_apicaltuft_L' % self.name],
                'diam': self.p_all['%s_apicaltuft_diam' % self.name],
                'cm': self.p_all['%s_dend_cm' % self.name],
                'Ra': self.p_all['%s_dend_Ra' % self.name],
            },
            'apical_oblique': {
                'L': self.p_all['%s_apicaloblique_L' % self.name],
                'diam': self.p_all['%s_apicaloblique_diam' % self.name],
                'cm': self.p_all['%s_dend_cm' % self.name],
                'Ra': self.p_all['%s_dend_Ra' % self.name],
            },
            'basal_1': {
                'L': self.p_all['%s_basal1_L' % self.name],
                'diam': self.p_all['%s_basal1_diam' % self.name],
                'cm': self.p_all['%s_dend_cm' % self.name],
                'Ra': self.p_all['%s_dend_Ra' % self.name],
            },
            'basal_2': {
                'L': self.p_all['%s_basal2_L' % self.name],
                'diam': self.p_all['%s_basal2_diam' % self.name],
                'cm': self.p_all['%s_dend_cm' % self.name],
                'Ra': self.p_all['%s_dend_Ra' % self.name],
            },
            'basal_3': {
                'L': self.p_all['%s_basal3_L' % self.name],
                'diam': self.p_all['%s_basal3_diam' % self.name],
                'cm': self.p_all['%s_dend_cm' % self.name],
                'Ra': self.p_all['%s_dend_Ra' % self.name],
            },
        }
        if self.name == 'L5Pyr':
            props.update({
                'apical_2': {
                    'L': self.p_all['L5Pyr_apical2_L'],
                    'diam': self.p_all['L5Pyr_apical2_diam'],
                    'cm': self.p_all['L5Pyr_dend_cm'],
                    'Ra': self.p_all['L5Pyr_dend_Ra'],
                },
            })
        return props

    def _get_syn_props(self):
        return {
            'ampa': {
                'e': self.p_all['%s_ampa_e' % self.name],
                'tau1': self.p_all['%s_ampa_tau1' % self.name],
                'tau2': self.p_all['%s_ampa_tau2' % self.name],
            },
            'nmda': {
                'e': self.p_all['%s_nmda_e' % self.name],
                'tau1': self.p_all['%s_nmda_tau1' % self.name],
                'tau2': self.p_all['%s_nmda_tau2' % self.name],
            },
            'gabaa': {
                'e': self.p_all['%s_gabaa_e' % self.name],
                'tau1': self.p_all['%s_gabaa_tau1' % self.name],
                'tau2': self.p_all['%s_gabaa_tau2' % self.name],
            },
            'gabab': {
                'e': self.p_all['%s_gabab_e' % self.name],
                'tau1': self.p_all['%s_gabab_tau1' % self.name],
                'tau2': self.p_all['%s_gabab_tau2' % self.name],
            }
        }

    def _synapse_create(self, p_syn):
        """Creates synapses onto this cell."""
        # Somatic synapses
        self.synapses['soma_gabaa'] = self.syn_create(self.soma(0.5),
                                                      **p_syn['gabaa'])
        self.synapses['soma_gabab'] = self.syn_create(self.soma(0.5),
                                                      **p_syn['gabab'])

        # Dendritic synapses
        self.synapses['apicaloblique_ampa'] = self.syn_create(
            self.dends['apical_oblique'](0.5), **p_syn['ampa'])
        self.synapses['apicaloblique_nmda'] = self.syn_create(
            self.dends['apical_oblique'](0.5), **p_syn['nmda'])

        self.synapses['basal2_ampa'] = self.syn_create(
            self.dends['basal_2'](0.5), **p_syn['ampa'])
        self.synapses['basal2_nmda'] = self.syn_create(
            self.dends['basal_2'](0.5), **p_syn['nmda'])

        self.synapses['basal3_ampa'] = self.syn_create(
            self.dends['basal_3'](0.5), **p_syn['ampa'])
        self.synapses['basal3_nmda'] = self.syn_create(
            self.dends['basal_3'](0.5), **p_syn['nmda'])

        self.synapses['apicaltuft_ampa'] = self.syn_create(
            self.dends['apical_tuft'](0.5), **p_syn['ampa'])
        self.synapses['apicaltuft_nmda'] = self.syn_create(
            self.dends['apical_tuft'](0.5), **p_syn['nmda'])

        if self.name == 'L5Pyr':
            self.synapses['apicaltuft_gabaa'] = self.syn_create(
                self.dends['apical_tuft'](0.5), **p_syn['gabaa'])

    # one parreceive function to handle all types of external parreceives
    # types must be defined explicitly here
    # this function handles evoked, gaussian, and poisson inputs
    def parreceive_ext(self, type, gid, gid_dict, pos_dict, p_ext):
        """Connect cell to external input."""
        if type.startswith(('evprox', 'evdist')):
            if self.celltype in p_ext.keys():
                gid_ev = gid + gid_dict[type][0]

                nc_dict = dict()
                # separate dictionaries for ampa and nmda evoked inputs
                nc_dict['ampa'] = {
                    'pos_src': pos_dict[type][gid],
                    # index 0 for ampa weight
                    'A_weight': p_ext[self.celltype][0],
                    'A_delay': p_ext[self.celltype][2],  # index 2 for delay
                    'lamtha': p_ext['lamtha_space'],
                    'threshold': p_ext['threshold'],
                    'type_src': type
                }

                nc_dict['nmda'] = {
                    'pos_src': pos_dict[type][gid],
                    # index 1 for nmda weight
                    'A_weight': p_ext[self.celltype][1],
                    'A_delay': p_ext[self.celltype][2],  # index 2 for delay
                    'lamtha': p_ext['lamtha_space'],
                    'threshold': p_ext['threshold'],
                    'type_src': type
                }

                # NEW: note that default/original is 0 nmda weight
                # for the proximal dends
                for receptor in ['ampa', 'nmda']:
                    self._connect_feed_at_loc(
                        feed_loc=p_ext['loc'], receptor=receptor,
                        gid_src=gid_ev, nc_dict=nc_dict[receptor],
                        nc_list=self.ncfrom_common)

        elif type == 'extgauss':
            # gid is this cell's gid
            # gid_dict is the whole dictionary, including the gids of
            # the extgauss
            # pos_list is also the pos of the extgauss (net origin)
            # p_ext_gauss are the params (strength, etc.)

            # gid shift is based on L2_pyramidal cells NOT L5
            # I recognize this is ugly (hack)
            # gid_shift = gid_dict['extgauss'][0] - gid_dict['L2_pyramidal'][0]
            if self.celltype in p_ext.keys():
                gid_extgauss = gid + gid_dict['extgauss'][0]

                nc_dict = {
                    'pos_src': pos_dict['extgauss'][gid],
                    # index 0 for ampa weight (nmda not yet used in Gauss)
                    'A_weight': p_ext[self.celltype][0],
                    'A_delay': p_ext[self.celltype][2],  # index 2 for delay
                    'lamtha': p_ext['lamtha'],
                    'threshold': p_ext['threshold'],
                    'type_src': type
                }

                self._connect_feed_at_loc(
                    feed_loc='proximal', receptor='ampa',
                    gid_src=gid_extgauss, nc_dict=nc_dict,
                    nc_list=self.ncfrom_extgauss)

        elif type == 'extpois':
            if self.celltype in p_ext.keys():
                gid_extpois = gid + gid_dict['extpois'][0]

                nc_dict = {
                    'pos_src': pos_dict['extpois'][gid],
                    # index 0 for ampa weight
                    'A_weight': p_ext[self.celltype][0],
                    'A_delay': p_ext[self.celltype][2],  # index 2 for delay
                    'lamtha': p_ext['lamtha_space'],
                    'threshold': p_ext['threshold'],
                    'type_src': type
                }

                self._connect_feed_at_loc(
                    feed_loc='proximal', receptor='ampa',
                    gid_src=gid_extpois, nc_dict=nc_dict,
                    nc_list=self.ncfrom_extpois)

                if p_ext[self.celltype][1] > 0.0:
                    # index 1 for nmda weight
                    nc_dict['A_weight'] = p_ext[self.celltype][1]

                    self._connect_feed_at_loc(
                        feed_loc='proximal', receptor='nmda',
                        gid_src=gid_extpois, nc_dict=nc_dict,
                        nc_list=self.ncfrom_extpois)

        else:
            print("Warning, ext type def does not exist in L2Pyr")

    # receive from common inputs
    # XXX check NetCon connections for proximal inputs with zero weights
    def parreceive(self, gid, gid_dict, pos_dict, p_ext):
        for gid_src, p_src, pos in zip(gid_dict['common'],
                                       p_ext, pos_dict['common']):
            for receptor in ['ampa', 'nmda']:
                # Check if AMPA params defined in p_src
                if f'{self.name}_{receptor}' in p_src.keys():
                    nc_dict = {
                        'pos_src': pos,
                        'A_weight': p_src[f'{self.name}_{receptor}'][0],
                        'A_delay': p_src[f'{self.name}_{receptor}'][1],
                        'lamtha': p_src['lamtha'],
                        'threshold': p_src['threshold'],
                        'type_src': 'ext'
                    }

                self._connect_feed_at_loc(
                    feed_loc=p_src['loc'], receptor=receptor,
                    gid_src=gid_src, nc_dict=nc_dict,
                    nc_list=self.ncfrom_common)


class L2Pyr(Pyr):
    """Layer 2 pyramidal cell class.

    Parameters
    ----------
    gid : int
        The cell id.
    p : dict
        The parameters dictionary.

    Attributes
    ----------
    name : str
        The name of the cell
    dends : dict
        The dendrites. The key is the name of the dendrite
        and the value is an instance of h.Section.
    list_dend : list of h.Section
        List of dendrites.
    """

    def __init__(self, gid=-1, pos=-1, p={}):
        # Get default L2Pyr params and update them with any
        # corresponding params in p
        p_all_default = get_L2Pyr_params_default()
        self.p_all = compare_dictionaries(p_all_default, p)

        # Get somatic, dendritic, and synapse properties
        p_soma = self._get_soma_props(pos)

        # usage: Pyr.__init__(self, soma_props)
        Pyr.__init__(self, gid, p_soma)

        p_dend = self._get_dend_props()
        p_syn = self._get_syn_props()

        self.celltype = 'L2_pyramidal'

        # geometry
        # creates dict of dends: self.dends
        self.create_dends(p_dend)
        self.topol()  # sets the connectivity between sections
        # sets geom properties;
        # adjusted after translation from hoc (2009 model)
        self.geom(p_dend)

        # biophysics
        self._biophys_soma()
        self._biophys_dends()

        # dipole_insert() comes from Cell()
        self.yscale = self.get_sectnames()
        self.dipole_insert(self.yscale)

        # create synapses
        self._synapse_create(p_syn)
        # self.__synapse_create()

        # run record_current_soma(), defined in Cell()
        self.record_current_soma()

    # Returns hardcoded somatic properties
    def _get_soma_props(self, pos):
        return {
            'pos': pos,
            'L': self.p_all['L2Pyr_soma_L'],
            'diam': self.p_all['L2Pyr_soma_diam'],
            'cm': self.p_all['L2Pyr_soma_cm'],
            'Ra': self.p_all['L2Pyr_soma_Ra'],
            'name': 'L2Pyr',
        }

    def geom(self, p_dend):
        """The geometry."""
        soma = self.soma
        dend = self.list_dend
        # increased by 70% for human
        soma.L = 22.1
        dend[0].L = 59.5
        dend[1].L = 340
        dend[2].L = 306
        dend[3].L = 238
        dend[4].L = 85
        dend[5].L = 255
        dend[6].L = 255
        soma.diam = 23.4
        dend[0].diam = 4.25
        dend[1].diam = 3.91
        dend[2].diam = 4.08
        dend[3].diam = 3.4
        dend[4].diam = 4.25
        dend[5].diam = 2.72
        dend[6].diam = 2.72
        # resets length,diam,etc. based on param specification
        self.set_dend_props(p_dend)

    def topol(self):
        """Connects sections of THIS cell together."""
        # child.connect(parent, parent_end, {child_start=0})
        # Distal (Apical)
        self.dends['apical_trunk'].connect(self.soma, 1, 0)
        self.dends['apical_1'].connect(self.dends['apical_trunk'], 1, 0)
        self.dends['apical_tuft'].connect(self.dends['apical_1'], 1, 0)

        # apical_oblique comes off distal end of apical_trunk
        self.dends['apical_oblique'].connect(self.dends['apical_trunk'], 1, 0)

        # Proximal (basal)
        self.dends['basal_1'].connect(self.soma, 0, 0)
        self.dends['basal_2'].connect(self.dends['basal_1'], 1, 0)
        self.dends['basal_3'].connect(self.dends['basal_1'], 1, 0)

        self.basic_shape()  # translated from original hoc (2009 model)

    def basic_shape(self):
        """Define shape of the neuron."""
        # THESE AND LENGHTHS MUST CHANGE TOGETHER!!!
        pt3dclear = h.pt3dclear
        pt3dadd = h.pt3dadd
        soma = self.soma
        dend = self.list_dend
        pt3dclear(sec=soma)
        pt3dadd(-50, 765, 0, 1, sec=soma)
        pt3dadd(-50, 778, 0, 1, sec=soma)
        pt3dclear(sec=dend[0])
        pt3dadd(-50, 778, 0, 1, sec=dend[0])
        pt3dadd(-50, 813, 0, 1, sec=dend[0])
        pt3dclear(sec=dend[1])
        pt3dadd(-50, 813, 0, 1, sec=dend[1])
        pt3dadd(-250, 813, 0, 1, sec=dend[1])
        pt3dclear(sec=dend[2])
        pt3dadd(-50, 813, 0, 1, sec=dend[2])
        pt3dadd(-50, 993, 0, 1, sec=dend[2])
        pt3dclear(sec=dend[3])
        pt3dadd(-50, 993, 0, 1, sec=dend[3])
        pt3dadd(-50, 1133, 0, 1, sec=dend[3])
        pt3dclear(sec=dend[4])
        pt3dadd(-50, 765, 0, 1, sec=dend[4])
        pt3dadd(-50, 715, 0, 1, sec=dend[4])
        pt3dclear(sec=dend[5])
        pt3dadd(-50, 715, 0, 1, sec=dend[5])
        pt3dadd(-156, 609, 0, 1, sec=dend[5])
        pt3dclear(sec=dend[6])
        pt3dadd(-50, 715, 0, 1, sec=dend[6])
        pt3dadd(56, 609, 0, 1, sec=dend[6])

    def _biophys_soma(self):
        """Adds biophysics to soma."""
        # set soma biophysics specified in Pyr
        # self.pyr_biophys_soma()

        # Insert 'hh2' mechanism
        self.soma.insert('hh2')
        self.soma.gkbar_hh2 = self.p_all['L2Pyr_soma_gkbar_hh2']
        self.soma.gl_hh2 = self.p_all['L2Pyr_soma_gl_hh2']
        self.soma.el_hh2 = self.p_all['L2Pyr_soma_el_hh2']
        self.soma.gnabar_hh2 = self.p_all['L2Pyr_soma_gnabar_hh2']

        # Insert 'km' mechanism
        # Units: pS/um^2
        self.soma.insert('km')
        self.soma.gbar_km = self.p_all['L2Pyr_soma_gbar_km']

    def _biophys_dends(self):
        """Defining biophysics for dendrites."""
        # set dend biophysics
        # iterate over keys in self.dends and set biophysics for each dend
        for key in self.dends:
            # neuron syntax is used to set values for mechanisms
            # sec.gbar_mech = x sets value of gbar for mech to x for all segs
            # in a section. This method is significantly faster than using
            # a for loop to iterate over all segments to set mech values

            # Insert 'hh' mechanism
            self.dends[key].insert('hh2')
            self.dends[key].gkbar_hh2 = self.p_all['L2Pyr_dend_gkbar_hh2']
            self.dends[key].gl_hh2 = self.p_all['L2Pyr_dend_gl_hh2']
            self.dends[key].gnabar_hh2 = self.p_all['L2Pyr_dend_gnabar_hh2']
            self.dends[key].el_hh2 = self.p_all['L2Pyr_dend_el_hh2']

            # Insert 'km' mechanism
            # Units: pS/um^2
            self.dends[key].insert('km')
            self.dends[key].gbar_km = self.p_all['L2Pyr_dend_gbar_km']

    def parconnect(self, gid, gid_dict, pos_dict, p):
        """Collect receptor-type-based connections here."""

        postsyns = [self.synapses['apicaloblique_ampa'],
                    self.synapses['basal2_ampa'],
                    self.synapses['basal3_ampa']]
        self._connect(gid, gid_dict, pos_dict, p,
                      'L2_pyramidal', 'L2Pyr', lamtha=3., receptor='ampa',
                      postsyns=postsyns, autapses=False)

        postsyns = [self.synapses['apicaloblique_nmda'],
                    self.synapses['basal2_nmda'],
                    self.synapses['basal3_nmda']]
        self._connect(gid, gid_dict, pos_dict, p,
                      'L2_pyramidal', 'L2Pyr', lamtha=3., receptor='nmda',
                      postsyns=postsyns, autapses=False)

        self._connect(gid, gid_dict, pos_dict, p,
                      'L2_basket', 'L2Basket', lamtha=50., receptor='gabaa',
                      postsyns=[self.synapses['soma_gabaa']])
        self._connect(gid, gid_dict, pos_dict, p,
                      'L2_basket', 'L2Basket', lamtha=50., receptor='gabab',
                      postsyns=[self.synapses['soma_gabab']])


# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted
# units for taur: ms

class L5Pyr(Pyr):
    """Layer 5 Pyramidal class.

    Attributes
    ----------
    name : str
        The name of the cell
    dends : dict
        The dendrites. The key is the name of the dendrite
        and the value is an instance of h.Section.
    list_dend : list of h.Section
        List of dendrites.
    """

    def __init__(self, gid=-1, pos=-1, p={}):
        """Get default L5Pyr params and update them with
            corresponding params in p."""
        p_all_default = get_L5Pyr_params_default()
        self.p_all = compare_dictionaries(p_all_default, p)

        # Get somatic, dendirtic, and synapse properties
        p_soma = self.__get_soma_props(pos)

        Pyr.__init__(self, gid, p_soma)
        p_dend = self._get_dend_props()
        p_syn = self._get_syn_props()

        self.celltype = 'L5Pyr'

        # Geometry
        # dend Cm and dend Ra set using soma Cm and soma Ra
        self.create_dends(p_dend)  # just creates the sections
        self.topol()  # sets the connectivity between sections
        # sets geom properties; adjusted after translation from
        # hoc (2009 model)
        self.geom(p_dend)

        # biophysics
        self.__biophys_soma()
        self.__biophys_dends()

        # Dictionary of length scales to calculate dipole without
        # 3d shape. Comes from Pyr().
        # dipole_insert() comes from Cell()
        self.yscale = self.get_sectnames()
        self.dipole_insert(self.yscale)

        # create synapses
        self._synapse_create(p_syn)

        # insert iclamp
        self.list_IClamp = []

        # run record current soma, defined in Cell()
        self.record_current_soma()

    def basic_shape(self):
        """The shape of the neuron."""
        # THESE AND LENGHTHS MUST CHANGE TOGETHER!!!
        pt3dclear = h.pt3dclear
        pt3dadd = h.pt3dadd
        dend = self.list_dend
        pt3dclear(sec=self.soma)
        pt3dadd(0, 0, 0, 1, sec=self.soma)
        pt3dadd(0, 23, 0, 1, sec=self.soma)
        pt3dclear(sec=dend[0])
        pt3dadd(0, 23, 0, 1, sec=dend[0])
        pt3dadd(0, 83, 0, 1, sec=dend[0])
        pt3dclear(sec=dend[1])
        pt3dadd(0, 83, 0, 1, sec=dend[1])
        pt3dadd(-150, 83, 0, 1, sec=dend[1])
        pt3dclear(sec=dend[2])
        pt3dadd(0, 83, 0, 1, sec=dend[2])
        pt3dadd(0, 483, 0, 1, sec=dend[2])
        pt3dclear(sec=dend[3])
        pt3dadd(0, 483, 0, 1, sec=dend[3])
        pt3dadd(0, 883, 0, 1, sec=dend[3])
        pt3dclear(sec=dend[4])
        pt3dadd(0, 883, 0, 1, sec=dend[4])
        pt3dadd(0, 1133, 0, 1, sec=dend[4])
        pt3dclear(sec=dend[5])
        pt3dadd(0, 0, 0, 1, sec=dend[5])
        pt3dadd(0, -50, 0, 1, sec=dend[5])
        pt3dclear(sec=dend[6])
        pt3dadd(0, -50, 0, 1, sec=dend[6])
        pt3dadd(-106, -156, 0, 1, sec=dend[6])
        pt3dclear(sec=dend[7])
        pt3dadd(0, -50, 0, 1, sec=dend[7])
        pt3dadd(106, -156, 0, 1, sec=dend[7])

    def geom(self, p_dend):
        """The geometry."""
        soma = self.soma
        dend = self.list_dend
        # soma.L = 13 # BUSH 1999 spike amp smaller
        soma.L = 39  # Bush 1993
        dend[0].L = 102
        dend[1].L = 255
        dend[2].L = 680  # default 400
        dend[3].L = 680  # default 400
        dend[4].L = 425
        dend[5].L = 85
        dend[6].L = 255  # default 150
        dend[7].L = 255  # default 150
        # soma.diam = 18.95 # Bush 1999
        soma.diam = 28.9  # Bush 1993
        dend[0].diam = 10.2
        dend[1].diam = 5.1
        dend[2].diam = 7.48  # default 4.4
        dend[3].diam = 4.93  # default 2.9
        dend[4].diam = 3.4
        dend[5].diam = 6.8
        dend[6].diam = 8.5
        dend[7].diam = 8.5
        # resets length,diam,etc. based on param specification
        self.set_dend_props(p_dend)

    def __get_soma_props(self, pos):
        """Sets somatic properties. Returns dictionary."""
        return {
            'pos': pos,
            'L': self.p_all['L5Pyr_soma_L'],
            'diam': self.p_all['L5Pyr_soma_diam'],
            'cm': self.p_all['L5Pyr_soma_cm'],
            'Ra': self.p_all['L5Pyr_soma_Ra'],
            'name': 'L5Pyr',
        }

    def topol(self):
        """Connects sections of this cell together."""

        # child.connect(parent, parent_end, {child_start=0})
        # Distal (apical)
        self.dends['apical_trunk'].connect(self.soma, 1, 0)
        self.dends['apical_1'].connect(self.dends['apical_trunk'], 1, 0)
        self.dends['apical_2'].connect(self.dends['apical_1'], 1, 0)
        self.dends['apical_tuft'].connect(self.dends['apical_2'], 1, 0)

        # apical_oblique comes off distal end of apical_trunk
        self.dends['apical_oblique'].connect(self.dends['apical_trunk'], 1, 0)

        # Proximal (basal)
        self.dends['basal_1'].connect(self.soma, 0, 0)
        self.dends['basal_2'].connect(self.dends['basal_1'], 1, 0)
        self.dends['basal_3'].connect(self.dends['basal_1'], 1, 0)

        self.basic_shape()  # translated from original hoc (2009 model)

    # adds biophysics to soma
    def __biophys_soma(self):
        # set soma biophysics specified in Pyr
        # self.pyr_biophys_soma()

        # Insert 'hh2' mechanism
        self.soma.insert('hh2')
        self.soma.gkbar_hh2 = self.p_all['L5Pyr_soma_gkbar_hh2']
        self.soma.gnabar_hh2 = self.p_all['L5Pyr_soma_gnabar_hh2']
        self.soma.gl_hh2 = self.p_all['L5Pyr_soma_gl_hh2']
        self.soma.el_hh2 = self.p_all['L5Pyr_soma_el_hh2']

        # insert 'ca' mechanism
        # Units: pS/um^2
        self.soma.insert('ca')
        self.soma.gbar_ca = self.p_all['L5Pyr_soma_gbar_ca']

        # insert 'cad' mechanism
        # units of tau are ms
        self.soma.insert('cad')
        self.soma.taur_cad = self.p_all['L5Pyr_soma_taur_cad']

        # insert 'kca' mechanism
        # units are S/cm^2?
        self.soma.insert('kca')
        self.soma.gbar_kca = self.p_all['L5Pyr_soma_gbar_kca']

        # Insert 'km' mechanism
        # Units: pS/um^2
        self.soma.insert('km')
        self.soma.gbar_km = self.p_all['L5Pyr_soma_gbar_km']

        # insert 'cat' mechanism
        self.soma.insert('cat')
        self.soma.gbar_cat = self.p_all['L5Pyr_soma_gbar_cat']

        # insert 'ar' mechanism
        self.soma.insert('ar')
        self.soma.gbar_ar = self.p_all['L5Pyr_soma_gbar_ar']

    def __biophys_dends(self):
        # set dend biophysics specified in Pyr()
        # self.pyr_biophys_dends()

        # set dend biophysics not specified in Pyr()
        for key in self.dends:
            # Insert 'hh2' mechanism
            self.dends[key].insert('hh2')
            self.dends[key].gkbar_hh2 = self.p_all['L5Pyr_dend_gkbar_hh2']
            self.dends[key].gl_hh2 = self.p_all['L5Pyr_dend_gl_hh2']
            self.dends[key].gnabar_hh2 = self.p_all['L5Pyr_dend_gnabar_hh2']
            self.dends[key].el_hh2 = self.p_all['L5Pyr_dend_el_hh2']

            # Insert 'ca' mechanims
            # Units: pS/um^2
            self.dends[key].insert('ca')
            self.dends[key].gbar_ca = self.p_all['L5Pyr_dend_gbar_ca']

            # Insert 'cad' mechanism
            self.dends[key].insert('cad')
            self.dends[key].taur_cad = self.p_all['L5Pyr_dend_taur_cad']

            # Insert 'kca' mechanism
            self.dends[key].insert('kca')
            self.dends[key].gbar_kca = self.p_all['L5Pyr_dend_gbar_kca']

            # Insert 'km' mechansim
            # Units: pS/um^2
            self.dends[key].insert('km')
            self.dends[key].gbar_km = self.p_all['L5Pyr_dend_gbar_km']

            # insert 'cat' mechanism
            self.dends[key].insert('cat')
            self.dends[key].gbar_cat = self.p_all['L5Pyr_dend_gbar_cat']

            # insert 'ar' mechanism
            self.dends[key].insert('ar')

        # set gbar_ar
        # Value depends on distance from the soma. Soma is set as
        # origin by passing self.soma as a sec argument to h.distance()
        # Then iterate over segment nodes of dendritic sections
        # and set gbar_ar depending on h.distance(seg.x), which returns
        # distance from the soma to this point on the CURRENTLY ACCESSED
        # SECTION!!!
        h.distance(sec=self.soma)

        for key in self.dends:
            self.dends[key].push()
            for seg in self.dends[key]:
                seg.gbar_ar = 1e-6 * np.exp(3e-3 * h.distance(seg.x))

            h.pop_section()

    # parallel connection function FROM all cell types TO here
    def parconnect(self, gid, gid_dict, pos_dict, p):

        postsyns = [self.synapses['apicaloblique_ampa'],
                    self.synapses['basal2_ampa'],
                    self.synapses['basal3_ampa']]
        self._connect(gid, gid_dict, pos_dict, p,
                      'L5Pyr', lamtha=3., receptor='ampa',
                      postsyns=postsyns, autapses=False)
        postsyns = [self.synapses['apicaloblique_nmda'],
                    self.synapses['basal2_nmda'],
                    self.synapses['basal3_nmda']]
        self._connect(gid, gid_dict, pos_dict, p,
                      'L5Pyr', lamtha=3., receptor='nmda',
                      postsyns=postsyns, autapses=False)

        self._connect(gid, gid_dict, pos_dict, p,
                      'L5_basket', 'L5Basket', lamtha=70., receptor='gabaa',
                      postsyns=[self.synapses['soma_gabaa']])
        self._connect(gid, gid_dict, pos_dict, p,
                      'L5_basket', 'L5Basket', lamtha=70., receptor='gabab',
                      postsyns=[self.synapses['soma_gabab']])

        postsyns = [self.synapses['basal2_ampa'],
                    self.synapses['basal3_ampa'],
                    self.synapses['apicaltuft_ampa'],
                    self.synapses['apicaloblique_ampa']]
        self._connect(gid, gid_dict, pos_dict, p,
                      'L2_pyramidal', 'L2Pyr', lamtha=3., postsyns=postsyns)

        self._connect(gid, gid_dict, pos_dict, p,
                      'L2_basket', 'L2Basket', lamtha=50.,
                      postsyns=[self.synapses['apicaltuft_gabaa']])
