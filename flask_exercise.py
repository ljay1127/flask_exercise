from flask import Flask, request
import requests as re
import numpy as np

# API URL
api_url = ''

# Flask initialization
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# List of valid values for sortBy and direction
sortBy_valid_values = ['id', 'reads', 'likes', 'popularity']
direction_valid_values = ['asc', 'desc']

# API request for tag data
def request_api_data(tag):
    response = re.get(
        api_url,
        params={'tag': tag}
    )

    # CONVERT CONTENT TO DICTIONARY
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Process tags passed by User
# Cleans each tag removing leading and trailing white spaces
def process_tags(tags):
    tags_list_temp = tags.split(',')
    tags_list = []
    for i in tags_list_temp:
        tags_list.append(i.strip())

    return tags_list

# Create a list of result from tags
def create_list_of_result(tags, sortBy, direction):
    # Split tags
    tags_list = process_tags(tags)

    # For building json files later
    author, authorId, id, likes, popularity, reads, tags = [], [], [], [], [], [], []

    # Temporary usage for data collection
    data = []

    # Collect data
    for tag in tags_list:
        new_data = request_api_data(tag)
        if new_data:
            data.append(new_data)

    # Parse Collected data
    for data_entry in data:
        for i in data_entry['posts']:
            if i['id'] not in id:
                author.append(i['author'])
                authorId.append(i['authorId'])
                id.append(i['id'])
                likes.append(i['likes'])
                popularity.append(i['popularity'])
                reads.append(i['reads'])
                tags.append(i['tags'])

    # Sort List for JSON creation
    tmp_np = None
    if sortBy == 'id':
        tmp_np = np.array(id)
    elif sortBy == 'reads':
        tmp_np = np.array(reads)
    elif sortBy == 'likes':
        tmp_np = np.array(likes)
    elif sortBy == 'popularity':
        tmp_np = np.array(popularity)

    index_order = np.argsort(tmp_np).tolist()

    # Implement descending order direction
    if direction == 'desc':
        index_order.reverse()

    # Create JSON File from List
    return_value = {}
    return_value['posts'] = []
    for i in index_order:
        return_value['posts'].append(
            {
                'id': id[i],
                'author': author[i],
                'authorId': authorId[i],
                'likes': likes[i],
                'popularity': popularity[i],
                'reads': reads[i],
                'tags': tags[i]
            }
        )

        
    if len(id) > 0:
        return return_value
    else:
        return {'result': 'No result found.'}

# Handles ping requests
@app.route('/api/ping', methods=['GET'])
def ping():
    return {'success': True}, 200

# Handles ping requests other than GET
@app.route('/api/ping', methods=[
    'POST', 'PUT', 'PATCH', 'DELETE', 'COPY',
    'LINK', 'UNLINK', 'PURGE', 'LOCK',
    'UNLOCK', 'PROPFIND', 'VIEW'
])
def ping_method_not_supported():
    return {'success': False}, 501

# handles posts requests
@app.route('/api/posts', methods=['GET'])
def posts():
    tags, sortBy, direction = None, None, 'asc'
    tags = request.args.get('tags')
    sortBy = request.args.get('sortBy')
    direction = request.args.get('direction')

    if not tags:
        return {'error': 'Tags parameter is required'}, 400
    elif sortBy not in sortBy_valid_values:
        return {'error': 'sortBy parameter is invalid'}, 400
    elif direction not in direction_valid_values:
        return {'error': 'sortBy parameter is invalid'}, 400
    else:
        return create_list_of_result(tags, sortBy, direction)

# handles posts requests other than GET
@app.route('/api/posts', methods=[
    'POST', 'PUT', 'PATCH', 'DELETE', 'COPY',
    'LINK', 'UNLINK', 'PURGE', 'LOCK',
    'UNLOCK', 'PROPFIND', 'VIEW'
])
def posts_method_not_supported():
    return {'success': False}, 501

# run Flask server
if __name__ == '__main__':
    app.run(port=1337)