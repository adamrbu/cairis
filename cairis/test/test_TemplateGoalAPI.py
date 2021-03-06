#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import logging
import json
from urllib import quote
from StringIO import StringIO
import os
import jsonpickle
import cairis.core.BorgFactory
from cairis.core.Borg import Borg
from cairis.core.TemplateGoal import TemplateGoal
from cairis.core.ValueTypeParameters import ValueTypeParameters
from cairis.core.TemplateAssetParameters import TemplateAssetParameters
from cairis.core.TemplateGoalParameters import TemplateGoalParameters
from cairis.test.CairisDaemonTestCase import CairisDaemonTestCase
from cairis.mio.ModelImport import importModelFile
from cairis.tools.JsonConverter import json_deserialize

__author__ = 'Shamal Faily'

def addTestData():
  f = open(os.environ['CAIRIS_SRC'] + '/test/templategoals.json')
  d = json.load(f)
  f.close()
  iAccessRights = d['access_rights']
  iSurfaceTypes = d['surface_type']
  iTemplateAssets = d['template_assets']
  iTemplateGoals = d['template_goals']
  cairis.core.BorgFactory.initialise()
  b = Borg()
  iar1 = ValueTypeParameters(iAccessRights[0]["theName"], iAccessRights[0]["theDescription"], 'access_right','',iAccessRights[0]["theValue"],iAccessRights[0]["theRationale"])
  ist1 = ValueTypeParameters(iSurfaceTypes[0]["theName"], iSurfaceTypes[0]["theDescription"], 'surface_type','',iSurfaceTypes[0]["theValue"],iSurfaceTypes[0]["theRationale"])
  b.dbProxy.addValueType(iar1)
  b.dbProxy.addValueType(ist1)
  spValues = [(0,'None'),(0,'None'),(0,'None'),(0,'None'),(0,'None'),(0,'None'),(0,'None'),(0,'None')]
  iTap = TemplateAssetParameters(iTemplateAssets[0]["theName"], iTemplateAssets[0]["theShortCode"], iTemplateAssets[0]["theDescription"], iTemplateAssets[0]["theSignificance"],iTemplateAssets[0]["theType"],iTemplateAssets[0]["theSurfaceType"],iTemplateAssets[0]["theAccessRight"],spValues,[],[])
  b.dbProxy.addTemplateAsset(iTap)
  iTag1 = TemplateGoalParameters(iTemplateGoals[0]["theName"],iTemplateGoals[0]["theDefinition"],iTemplateGoals[0]["theRationale"],iTemplateGoals[0]["theConcerns"],iTemplateGoals[0]["theResponsibilities"])
  b.dbProxy.addTemplateGoal(iTag1)

class TemplateGoalAPITests(CairisDaemonTestCase):

  @classmethod
  def setUpClass(cls):
    importModelFile(os.environ['CAIRIS_SRC'] + '/../examples/exemplars/ACME_Water/ACME_Water.xml',1,'test')
    addTestData() 

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.new_tg = TemplateGoal(
      goalId = '-1',
      goalName = 'Test template goal',
      goalDef = 'A definition',
      goalRat = 'A rationale',
      goalConcerns = [],
      goalResp = [])
    self.new_tg_dict = {
      'session_id' : 'test',
      'object': self.new_tg
    }
    self.existing_tg_name = 'Qualified data use'

  def test_get_all(self):
    method = 'test_get'
    url = '/api/template_goals?session_id=test'
    self.logger.info('[%s] URL: %s', method, url)
    rv = self.app.get(url)
    tgs = jsonpickle.decode(rv.data)
    self.assertIsNotNone(tgs, 'No results after deserialization')
    self.assertIsInstance(tgs, dict, 'The result is not a dictionary as expected')
    self.assertGreater(len(tgs), 0, 'No template goals in the dictionary')
    self.logger.info('[%s] Template goals found: %d', method, len(tgs))
    tg = tgs.values()[0]
    self.logger.info('[%s] First template goal: %s \n', method, tg['theName'])

  def test_get_by_name(self):
    method = 'test_get_by_name'
    url = '/api/template_goals/name/%s?session_id=test' % quote(self.existing_tg_name)
    rv = self.app.get(url)
    self.assertIsNotNone(rv.data, 'No response')
    self.logger.debug('[%s] Response data: %s', method, rv.data)
    tg = jsonpickle.decode(rv.data)
    self.assertIsNotNone(tg, 'No results after deserialization')
    self.logger.info('[%s] Template goal: %s \n', method, tg['theName'])

  def test_post(self):
    method = 'test_post_new'
    rv = self.app.post('/api/template_goals', content_type='application/json', data=jsonpickle.encode(self.new_tg_dict))
    self.logger.debug('[%s] Response data: %s', method, rv.data)
    json_resp = json_deserialize(rv.data)
    self.assertIsNotNone(json_resp, 'No results after deserialization')
    ackMsg = json_resp.get('message', None)
    self.assertEqual(ackMsg, 'Template Goal successfully added')

  def test_put(self):
    method = 'test_put'
    self.new_tg_dict['object'].theDefinition = 'Updated definition'
    url = '/api/template_goals/name/%s?session_id=test' % quote(self.existing_tg_name)
    rv = self.app.put(url, content_type='application/json', data=jsonpickle.encode(self.new_tg_dict))
    self.logger.debug('[%s] Response data: %s', method, rv.data)
    json_resp = json_deserialize(rv.data)
    self.assertIsNotNone(json_resp, 'No results after deserialization')
    ackMsg = json_resp.get('message', None)
    self.assertEqual(ackMsg, 'Template Goal successfully updated')

  def test_delete(self):
    method = 'test_delete'

    rv = self.app.post('/api/template_goals', content_type='application/json', data=jsonpickle.encode(self.new_tg_dict))
    self.logger.debug('[%s] Response data: %s', method, rv.data)
    json_resp = json_deserialize(rv.data)

    url = '/api/template_goals/name/%s?session_id=test' % quote(self.new_tg.theName)
    rv = self.app.delete(url)

    self.logger.debug('[%s] Response data: %s', method, rv.data)
    json_resp = json_deserialize(rv.data)
    self.assertIsNotNone(json_resp, 'No results after deserialization')
    ackMsg = json_resp.get('message', None)
    self.assertEqual(ackMsg, 'Template Goal successfully deleted')
