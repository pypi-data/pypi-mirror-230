#    Copyright 2020 Jonas Waeber
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from init_client import world_id, client

if __name__ == '__main__':
    template = client.block_template.get('3381', 1)
    print(template)

    test_block_template_1 = client.block_template.put(
        {
            "title": "5e TEST Block Template",
            "formSchemaParser": "json",
            "formSchema": '{"version":"1","system":"fate","author":{"username":"SoulLink","email":"jonaswaeber@gmail.com"},"unique_reference":"average_nameless_npc-soullink-4","name":"Average Nameless NPC","display_template":"","description":"The weakest of all adversary. Exist to make the players look awesome!","fields":{"name":{"input":"string","label":"Name","placeholder":"The name of theAverage Nameless NPC","required":true},"character_aspect_1":{"input":"string","label":"Character Aspect 1","description":"A generic aspect that can be used against this character.","placeholder":""},"character_aspect_2":{"input":"string","label":"Character Aspect 2","description":"An additional character aspect.","placeholder":""},"average_1_skill_1":{"input":"select","label":"Average (+1) Skill 1","description":"Should support whatever this NPC is going to use to compete in a conflict, contest or challenge.","placeholder":"","options":{"None":"None","Athletics":"Athletics","Burglary":"Burglary","Contacts":"Contacts","Crafts":"Crafts","Deceive":"Deceive","Drive":"Drive","Empathy":"Empathy","Fight":"Fight","Investigate":"Investigate","Lore":"Lore","Notice":"Notice","Physique":"Physique","Provoke":"Provoke","Rapport":"Rapport","Resources":"Resources","Shoot":"Shoot","Stealth":"Stealth","Will":"Will"}},"average_1_skill_2":{"input":"select","label":"Average (+1) Skill 2","description":"An additional support skill.","placeholder":"","options":{"None":"None","Athletics":"Athletics","Burglary":"Burglary","Contacts":"Contacts","Crafts":"Crafts","Deceive":"Deceive","Drive":"Drive","Empathy":"Empathy","Fight":"Fight","Investigate":"Investigate","Lore":"Lore","Notice":"Notice","Physique":"Physique","Provoke":"Provoke","Rapport":"Rapport","Resources":"Resources","Shoot":"Shoot","Stealth":"Stealth","Will":"Will"}}}}',
            "RPGSRD": {
                "id": 1
            }
        }
    )
    test_block_template_2 = client.block_template.put(
        {
            'title': 'Test block_template Creation 2',
            'templateType': 'block_template',
            'world': {
                'id': world_id}
        }
    )
    response_patch_block_template_2 = client.block_template.patch(
        test_block_template_2['id'],
        {
            'excerpt': 'This is an excerpt for an block_template.'
        }
    )

    full_test_block_template_2 = client.block_template.get(
        test_block_template_2['id'],
        2
    )

    assert full_test_block_template_2['excerpt'] == 'This is an excerpt for an block_template.'

    client.block_template.delete(test_block_template_1['id'])
    client.block_template.delete(test_block_template_2['id'])

    block_template_with_a_lot_of_views = client.block_template.put(
        {
            'title': 'An block_template with a lot of views.',
            'templateType': 'block_template',
            'world': {
                'id': world_id
            }
        }
    )
    print(client.block_template.get(block_template_with_a_lot_of_views['id'], 2))
