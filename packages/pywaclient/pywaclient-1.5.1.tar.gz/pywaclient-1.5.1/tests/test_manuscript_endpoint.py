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

    manuscript_1 = client.manuscript.put(
        {
            'title': 'Test Manuscript Creation',
            'world': {
                'id': world_id}

        })

    client.manuscript.tag.put(
        {
            'manuscript': {
                'id': manuscript_1['id']
            },
            'title': 'Test Manuscript Tag Creation',
        })

    for manuscript_tag in client.manuscript.tags(manuscript_1['id']):
        print(manuscript_tag)

    client.manuscript.label.put(
        {
            'manuscript': {
                'id': manuscript_1['id']
            },
            'title': 'Test Manuscript Label Creation',
        })

    for manuscript_label in client.manuscript.labels(manuscript_1['id']):
        print(manuscript_label)

    # for manuscript_bookmark in client.manuscript.bookmarks(manuscript_1['id']):
    #     print(manuscript_bookmark)

    client.manuscript.version.put(
        {
            'manuscript': {
                'id': manuscript_1['id']
            },
            'title': 'Test Manuscript Version Creation',
        }
    )



    for manuscript_version in client.manuscript.versions(manuscript_1['id']):
        print(manuscript_version)

        client.manuscript.version.part.put(
            {
                'version': {
                    'id': manuscript_version['id']
                },
                'type': 'folder',
                'title': 'Test Manuscript Part Folder Creation',
            }
        )
        client.manuscript.version.part.put(
            {
                'version': {
                    'id': manuscript_version['id']
                },
                'type': 'richMediaUrl',
                'title': 'Test Manuscript Part Image Creation',
            }
        )
        client.manuscript.version.part.put(
            {
                'version': {
                    'id': manuscript_version['id']
                },
                'type': 'text',
                'title': 'Test Manuscript Part Image Creation',
            }
        )

        for manuscript_part in client.manuscript.version.parts(manuscript_version['id']):
            print(client.manuscript.version.part.get(manuscript_part['id'], 2))

            client.manuscript.version.part.beat.put(
                {
                    'part': {
                        'id': manuscript_part['id']
                    },
                    'title': 'Test Manuscript Beat Creation',
                }
            )

            for manuscript_beat in client.manuscript.version.part.beats(manuscript_part['id']):
                print(client.manuscript.version.part.beat.get(manuscript_beat['id'], 2))



        for manuscript_plot in client.manuscript.version.plots(manuscript_version['id']):
            print(manuscript_plot)

        for manuscript_stat in client.manuscript.version.stats(manuscript_version['id']):
            print(manuscript_stat)
    print(manuscript_1)
    full_manuscript_1 = client.manuscript.get(manuscript_1['id'], 3)

    print(full_manuscript_1)
    client.manuscript.delete(manuscript_1['id'])
