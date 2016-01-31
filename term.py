
import config
import template

import log
import util

from page import DynamicPage

################################################
# CompanyTerm
################################################

class Term:

  def __init__(self, page):
    self.term_page = page
    self.term_type = None
    self.builder = page.builder

    self.name = None

    self.manufacturers = []
    self.locations = []
    self.rockets = []
    self.spacecraft = []
    self.stages = []
    self.engines = []

  def get_unique_identifier(self):
    return self.term_page.get_unique_identifier()

  def get_name(self):
    return self.name or self.term_page.get_title()

  def set_name(self, name):
    self.name = name

  ########################
  #
  ########################

  def add(self, term):
    if type(term) is CompanyTerm:
      self.add_manufacturer(term.term_page)
    elif type(term) is RocketTerm:
      self.add_rocket(term.term_page)
    elif type(term) is SpacecraftTerm:
      self.add_spacecraft(term.term_page)
    elif type(term) is EngineTerm:
      self.add_engine(term.term_page)

  def add_manufacturer(self, slug):
    self.manufacturers.append(slug)

  def add_location(self, slug):
    self.locations.append(slug)

  def add_rocket(self, slug):
    self.rockets.append(slug)

  def add_spacecraft(self, slug):
    self.spacecraft.append(slug)

  def add_stage(self, slug):
    self.stages.append(slug)

  def add_engine(self, slug):
    self.engines.append(slug)

  def get_engines(self):
    return self.engines

  def parse_header_line(self, key, value):
    if key == 'name':
      self.set_name(value)
    elif key == 'manufacturer':
      self.add_manufacturer(value)
    elif key == 'location':
      self.add_location(value)
    elif key == 'rocket':
      self.add_rocket(value)
    elif key == 'spacecraft':
      self.add_spacecraft(value)
    elif key == 'stage':
      self.add_stage(value)
    elif key == 'engine':
      self.add_engine(value)
    else:
      return False
    return True

  def parse(self):
    self.engines.extend(self.get_engines())
  
  ########################
  # THINGS
  ########################

  # given a list of slugs, returns the thing
  def get_things(self, slugs, name, thing_type):
    things = []
    for slug in slugs:
      if type(slug) is not type(''):
        things.append(slug)
        continue
      thing = self.builder.get_term(slug)
      if not thing:
        log.warning(name + ' "' + slug + '" not found', self.term_page.get_unique_identifier())
        continue
      if not thing.term:
        log.warning(name + ' "' + slug + '" has no term information', self.term_page.get_unique_identifier())
        continue
      if type(thing.term) is not thing_type:
        log.warning('page "' + slug + '" is not of type ' + name, self.term_page.get_unique_identifier())
        continue
      things.append(thing)
    return things

  def collect(self):
    self.manufacturers = self.get_things(self.manufacturers, 'manufacturer', CompanyTerm)
    self.rockets = self.get_things(self.rockets, 'rocket', RocketTerm)
    self.spacecraft = self.get_things(self.spacecraft, 'spacecraft', SpacecraftTerm)
    self.engines = self.get_things(self.engines, 'engine', EngineTerm)
    self.stages = self.get_things(self.stages, 'stage', StageTerm)

    for m in self.manufacturers:
      term = m.get_term()
      if term: term.add(self)

  def post_collect(self):
    self.engines = self.get_engines()

  ########################
  # ARGS
  ########################

  def get_arg(self, key):
    if key == 'term-name':
      return self.get_name()
    elif key == 'term-link':
      return self.term_page.path.get_link_path()
    elif key == 'term-sidebar-contents':
      return self.get_sidebar_html()
    
  # run by the template while rendering; required_args is a list
  # of arguments that Page must provide

  ########################
  # SIDEBAR HTML
  ########################

  def get_sidebar_list(self, things, thing_name):
    if not things:
      return ''
    
    title = self.term_page.get_string('term-type-' + thing_name)
    if len(things) > 1:
      title = self.term_page.get_string('term-type-' + thing_name + '-plural')
    
    args = {}
    args['sidebar-list-title'] = title
    args['sidebar-list-classes'] = thing_name
    args['sidebar-list-items'] = ''.join([x.term.get_sidebar_item() for x in things])
    
    return self.builder.templates.render('term-sidebar-list.html', self, args)

  def get_sidebar_html(self):
    html = ''
    html += self.get_sidebar_list(self.manufacturers, 'manufacturer')
    return html

  def get_sidebar_item(self):
    return self.get_name()

################################################
# Object
################################################

class ObjectTerm(Term):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'object'

    self.mass = {
      'dry': 0,
      'wet': 0
    }

  def get_mass(self, dry=True):
    t = 'wet'
    if dry:
      t = 'dry'
    return self.mass[t]
      
  def get_mass_string(self, dry=True):
    return str(int(self.get_mass(dry)) or self.term_page.get_string('object-mass-unknown')) + self.term_page.get_string('kg')

  def set_mass(self, value, dry=True):
    t = 'wet'
    if dry:
      t = 'dry'
    s = value.split(None, 1)
    if len(s) == 2:
      t = s[0]
      value = s[1]
    self.mass[t] = float(value)

  def get_arg(self, key):
    if key == 'object-mass':
      return self.get_mass_string(True)
    elif key == 'object-mass-dry':
      return self.get_mass_string(True)
    elif key == 'object-mass-wet':
      return self.get_mass_string(False)
    else:
      return super().get_arg(key)
    
  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return True
    elif key == 'mass':
      self.set_mass(value, True)
    else:
      return False
    return True

################################################
# Vehicle
################################################

class VehicleTerm(ObjectTerm):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'vehicle'

    self.stages = []

    self.configurations = []

    self.stage_number = None

    self.payload = {
      'leo': 0,
      'gto': 0
    }

  def get_engines(self):
    engines = super().get_engines()
    
    for c in self.configurations:
      engines.extend(c.get_term().get_engines())

    return engines
      
  def set_payload(self, value):
    dest, kgs = value.lower().split(None, 1)
    self.payload[dest] = float(kgs)

  def get_payload(self, dest):
    return self.payload.get(dest) or 0

  def get_payload_string(self, dest):
    return str(int(self.get_payload(dest))) + ' ' + self.term_page.get_string('kg')

  def get_stage_number(self):
    return self.stage_number or str(len(self.stages))

  def set_stage_number(self, stage_number):
    self.stage_number = stage_number

  def get_arg(self, key):
    if key == 'configuration-name':
      return self.get_name()
    elif key == 'configuration-stages':
      return self.get_stage_number()
    else:
      return super().get_arg(key)
    
  def add_configuration(self, slug):
    self.configurations.append(slug)

  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return True
    elif key == 'stages':
      self.set_stage_number(value)
    elif key == 'configuration':
      self.add_configuration(value)
    elif key == 'payload':
      self.set_payload(value)
    else:
      return False
    return True

  def collect(self):
    super().collect()
    
    self.configurations = self.get_things(self.configurations, 'configuration', ConfigurationTerm)

################################################
# Engine
################################################

class EngineTerm(ObjectTerm):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'engine'

    self.engine_type = None

    self.vacuum_only = False

    self.thrust = [0, 0]
    self.isp = [0, 0]

  ########################
  
  def set_isp(self, value):
    values = value.lower().split(None, 1)
    self.isp = [float(x) for x in values]

  def get_isp(self, vac=False):
    if vac:
      return self.isp[1]
    return self.isp[0]
  
  def get_isp_string(self, vac=False):
    return str(int(self.get_isp(vac)) or self.term_page.get_string('engine-isp-unknown'))

  ########################
  
  def set_thrust(self, value):
    values = value.lower().split(None, 1)
    self.thrust = [float(x) for x in values]

  def get_thrust(self, vac=False):
    if vac:
      return self.thrust[1]
    return self.thrust[0]

  def get_thrust_string(self, vac=False):
    return str(self.get_thrust(vac) or self.term_page.get_string('engine-thrust-unknown')) + ' ' + self.term_page.get_string('kn')

  ########################
  
  def set_engine_vacuum_only(self, boolean):
    self.vacuum_only = util.boolean(boolean)
    
  def set_engine_type(self, engine_type):
    if engine_type in ['liquid', 'solid']:
      self.engine_type = engine_type
    else:
      log.warning('incorrect engine type "' + engine_type + '"', self.get_unique_identifier())
    return self.engine_type or self.term_page.get_string('engine-type-unknown')

  def get_engine_type(self):
    return self.term_page.get_string('engine-type-' + (self.engine_type or 'unknown'))

  ########################
  
  def set_engine_fuel(self, engine_fuel):
    self.engine_fuel = engine_fuel

  def set_engine_oxidizer(self, engine_oxidizer):
    self.engine_oxidizer = engine_oxidizer

  ########################
  
  def get_engine_fuel(self, abbreviation=False):
    if self.engine_fuel:
      if abbreviation:
        return self.engine_fuel.get_abbreviation()
      return self.engine_fuel.get_title()
    else:
      return self.term_page.get_string('engine-fuel-unknown')
    
  def get_engine_oxidizer(self, abbreviation=False):
    if self.engine_oxidizer:
      if abbreviation:
        return self.engine_oxidizer.get_abbreviation()
      return self.engine_oxidizer.get_title()
    else:
      return self.term_page.get_string('engine-oxidizer-unknown')

  ########################
  
  def get_engine_fuel_link(self):
    if self.engine_fuel:
      return self.engine_fuel.get_link_path()
    else:
      return ''

  def get_engine_oxidizer_link(self):
    if self.engine_oxidizer:
      return self.engine_oxidizer.get_link_path()
    else:
      return ''

  def get_engine_twr(self, dry=True, vac=False):
    mass = self.get_mass(dry)
    thrust = self.get_thrust(vac) * 1000 # kn to n
    thrust /= 9.81
    
    return thrust/mass

  ########################
    
  def get_arg(self, key):
    if key == 'engine-name':
      return self.get_name()
    elif key == 'engine-thrust':
      return self.get_thrust()
    
    elif key == 'engine-mass':
      return self.get_mass_string(True)
    
    elif key == 'string-engine-twr-sea-level':
      return self.term_page.get_string('engine-twr-sea-level')
    elif key == 'string-engine-twr-vacuum':
      return self.term_page.get_string('engine-twr-vacuum')
    
    elif key == 'engine-twr-sea-level':
      return str(int(self.get_engine_twr(True, False)))
    
    elif key == 'engine-twr-vacuum':
      return str(int(self.get_engine_twr(True, True)))
    
    elif key == 'engine-type':
      return self.get_engine_type()
    
    elif key == 'engine-vacuum-only':
      if self.vacuum_only:
        return 'vacuum-only'
      return ''
    
    elif key == 'string-engine-fuel-type':
      return self.term_page.get_string('engine-fuel-type')
    elif key == 'string-engine-oxidizer-type':
      return self.term_page.get_string('engine-oxidizer-type')
    
    elif key == 'engine-fuel':
      return self.get_engine_fuel()
    elif key == 'engine-oxidizer':
      return self.get_engine_oxidizer()
    
    elif key == 'engine-fuel-short':
      return self.get_engine_fuel(True)
    elif key == 'engine-oxidizer-short':
      return self.get_engine_oxidizer(True)
    
    elif key == 'engine-fuel-link':
      return self.get_engine_fuel_link()
    elif key == 'engine-oxidizer-link':
      return self.get_engine_oxidizer_link()
    
    elif key == 'string-engine-thrust-sea-level':
      return self.term_page.get_string('thrust-sea-level')
    elif key == 'string-engine-thrust-vacuum':
      return self.term_page.get_string('thrust-vacuum')
    
    elif key == 'string-engine-isp-sea-level':
      return self.term_page.get_string('isp-sea-level')
    elif key == 'string-engine-isp-vacuum':
      return self.term_page.get_string('isp-vacuum')
    
    elif key == 'engine-thrust-sea-level':
      return self.get_thrust_string(False)
    elif key == 'engine-thrust-vacuum':
      return self.get_thrust_string(True)
    
    elif key == 'engine-isp-sea-level':
      return self.get_isp_string(False)
    elif key == 'engine-isp-vacuum':
      return self.get_isp_string(True)
    
    else:
      return super().get_arg(key)
    
  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return True
    elif key == 'engine-type':
      self.set_engine_type(value)
    elif key == 'engine-vacuum-only':
      self.set_engine_vacuum_only(value)
    elif key == 'engine-fuel':
      self.set_engine_fuel(value)
    elif key == 'engine-oxidizer':
      self.set_engine_oxidizer(value)
    elif key == 'engine-thrust':
      self.set_thrust(value)
    elif key == 'engine-isp':
      self.set_isp(value)
    else:
      return False
    return True

  def get_sidebar_html(self):
    html = ''
    html += self.get_sidebar_list(self.manufacturers, 'manufacturer')
    html += self.get_sidebar_list(self.stages, 'stage')
    html += self.builder.templates.render('term-sidebar-engine.html', self)
    html += self.get_sidebar_list(self.engines, 'engine-family')
    return html

  def get_sidebar_item(self):
    return self.builder.templates.render('term-sidebar-item-engine.html', self)

  def collect(self):
    super().collect()
    
    self.engine_fuel = self.builder.get_term(self.engine_fuel)
    self.engine_oxidizer = self.builder.get_term(self.engine_oxidizer)

    if not self.engine_fuel:
      log.warning('no fuel type given', self.get_unique_identifier())
    if not self.engine_oxidizer:
      log.warning('no oxidizer type given', self.get_unique_identifier())

################################################
# Rocket
################################################

class RocketTerm(VehicleTerm):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'rocket'

  def get_lift_class(self):
    leo = self.payload['leo']
    if leo == 0:
      return self.term_page.get_string('not-available')
    elif leo < 2000:
      return 'SLV'
    elif leo < 20000:
      return 'MLV'
    elif leo < 50000:
      return 'HLV'
    else:
      return 'SHLV'

  def get_arg(self, key):
    if key == 'rocket-name':
      return self.get_name()
    elif key == 'rocket-class':
      return self.get_lift_class()
    else:
      return super().get_arg(key)
    
  def get_sidebar_html(self):
    html = ''
    html += self.get_sidebar_list(self.manufacturers, 'manufacturer')
    html += self.get_sidebar_list(self.configurations, 'configuration')
    html += self.get_sidebar_list(self.engines, 'engine')
    return html

  def get_sidebar_item(self):
    return self.builder.templates.render('term-sidebar-item-rocket.html', self)

################################################
# Spacecraft
################################################

class SpacecraftTerm(VehicleTerm):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'spacecraft'

  def get_sidebar_item(self):
    return self.builder.templates.render('term-sidebar-item-spacecraft.html', self)

  def get_arg(self, key):
    if key == 'spacecraft-name':
      return self.get_name()
    else:
      return super().get_arg(key)
    
  def get_sidebar_html(self):
    html = ''
    html += self.get_sidebar_list(self.manufacturers, 'manufacturer')
    html += self.get_sidebar_list(self.configurations, 'configuration')
    html += self.get_sidebar_list(self.rockets, 'rocket')
    return html

################################################
# Stage
################################################

class StageTerm(VehicleTerm):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'stage'

  def get_arg(self, key):
    if key == 'stage-name':
      return self.get_name()
    else:
      return super().get_arg(key)
    
  def get_sidebar_html(self):
    html = ''
    html += self.get_sidebar_list(self.manufacturers, 'manufacturer')
    html += self.get_sidebar_list(self.configurations, 'configuration-stage-used-on')
    html += self.get_sidebar_list(self.rockets, 'rocket-stage-used-on')
    html += self.get_sidebar_list(self.engines, 'engine')
    return html

  def get_sidebar_item(self):
    return self.builder.templates.render('term-sidebar-item-stage.html', self)

################################################
# Configuration
################################################

class ConfigurationTerm(VehicleTerm):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'configuration'

  def get_engines(self):
    engines = []
    for stage in self.stages:
      if stage.get_term():
        engines.extend(stage.get_term().get_engines())
    return engines

  def get_arg(self, key):
    if key == 'string-payload-leo':
      return self.term_page.get_string('payload-leo')
    elif key == 'string-payload-gto':
      return self.term_page.get_string('payload-gto')
    elif key == 'string-payload-tmi':
      return self.term_page.get_string('payload-tmi')
    elif key == 'payload-leo':
      return self.get_payload_string('leo')
    elif key == 'payload-gto':
      return self.get_payload_string('gto')
    elif key == 'payload-tmi':
      return self.get_payload_string('tmi')
    return super().get_arg(key)

  def get_sidebar_html(self):
    html = ''
    html += self.get_sidebar_list(self.manufacturers, 'manufacturer')
    html += self.get_sidebar_list(self.stages, 'stage')
    html += self.get_sidebar_list(self.rockets, 'rocket')
    html += self.get_sidebar_list(self.engines, 'engine')
    html += self.builder.templates.render('term-sidebar-configuration.html', self)
    return html

  def get_sidebar_item(self):
    return self.builder.templates.render('term-sidebar-item-configuration.html', self)

  def post_collect(self):
    for s in self.stages:
      term = s.get_term()
      if term: term.add_configuration(self.term_page)

################################################
# CompanyTerm
################################################

class CompanyTerm(Term):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'company'
    self.founding_date = None

  def get_arg(self, key):
    if key == 'company-name':
      return self.get_name()
    elif key == 'company-founding-date':
      return self.founding_date or self.term_page.get_string('term-type-company-founding-date-unknown')
    return super().get_arg(key)

  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return True
    elif key == 'founding-date':
      self.founding_date = value
    else:
      return False
    return True

  def get_sidebar_html(self):
    html = ''
    html += self.get_sidebar_list(self.rockets, 'rocket')
    html += self.get_sidebar_list(self.spacecraft, 'spacecraft')
    return html

  def get_sidebar_item(self):
    return self.builder.templates.render('term-sidebar-item-company.html', self)

################################################
# PropellantTerm
################################################

class PropellantTerm(Term):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'propellant'

    self.temperature = {}

    self.density = 0
    
  def get_arg(self, key):
    if key == 'propellant-density':
      return self.get_density_string()
    elif key == 'string-propellant-density':
      return self.term_page.get_string('propellant-density')
    else:
      return super().get_arg(key)
    
  def get_temperature(self, name):
    return self.temperature.get(name, None)
      
  def get_temperature_string(self, name):
    temp = self.get_temperature(name)
    if temp == None: temp = self.term_page.get_string('temperature-unknown')
    else: temp = '{0:02}'.format(temp)
    return str(temp) + self.term_page.get_string('temperature-centigrade')

  def set_temperature(self, value, name=None):
    s = value.split(None, 1)
    if len(s) == 2:
      name = s[0]
      value = s[1]
    if not name:
      log.warning('expected name with temperature', self.get_unique_identifier())
      return
    self.temperature[name] = float(value)

  ########################

  def get_density(self):
    return self.density

  def get_density_string(self):
    return str(self.get_density()) + ' ' + self.term_page.get_string('kg-per-cubic-meter')

  ########################

  def set_density(self, value):
    self.density = float(value) # kg/m3

  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return True
    elif key == 'temperature':
      self.set_temperature(value)
    elif key == 'density':
      self.set_density(value)
    else:
      return False
    return True

  def get_sidebar_html(self):
    html = ''
    html += self.builder.templates.render('term-sidebar-propellant.html', self)
    return html

  def get_sidebar_item(self):
    return self.builder.templates.render('term-sidebar-item-company.html', self)

################################################
# TermPage
################################################

class TermPage(DynamicPage):

  def __init__(self, builder, input_path):
    super().__init__(builder, input_path)
    self.output_root = self.builder.languages.get(self.language, 'page-term-slug')
    
    self.term = None

  ########################

  def get_term_sidebar_html(self):
    return self.term.get_sidebar_html()

  ########################

  def get_arg(self, key):
    if key == 'term-name':
      return self.title
    elif key == 'term-link':
      return self.path.get_link_path()
    elif key == 'term-sidebar':
      if self.term:
        return self.builder.templates.render('term-sidebar.html', self)
      log.warning('no term information', self.get_unique_identifier())
      return ''
    elif key == 'term-sidebar-contents':
      return self.get_term_sidebar_html()
    elif key == 'page-contents':
      return self.builder.templates.render('term.html', self)
    return super().get_arg(key)

  def collect(self):
    if self.term:
      self.term.collect()

  def post_collect(self):
    if self.term:
      self.term.post_collect()

  def get_term(self):
    if not self.term: return None
    return self.term
  
  def set_term_type(self, term_type):
    if term_type == 'company':
      self.term = CompanyTerm(self)
    elif term_type == 'rocket':
      self.term = RocketTerm(self)
    elif term_type == 'spacecraft':
      self.term = SpacecraftTerm(self)
    elif term_type == 'stage':
      self.term = StageTerm(self)
    elif term_type == 'engine':
      self.term = EngineTerm(self)
    elif term_type in ['fuel', 'oxidizer', 'prop', 'propellant']:
      self.term = PropellantTerm(self)
    elif term_type in ['configuration', 'config']:
      self.term = ConfigurationTerm(self)
    else:
      log.warning('unknown term type "' + term_type + '"', self.get_unique_identifier())

  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return True
    elif key == 'type':
      self.set_term_type(value)
    elif self.term:
      return self.term.parse_header_line(key, value)
    else:
      return False
    return True
      
  def get_inline_html(self):
    return self.builder.templates.render('term-inline.html', self)
    
  def get_term_link(self):
    return self.path.get_link_path()
    
