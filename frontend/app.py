import csv
import io
import re
import numpy as np
import matplotlib.pyplot as plt
import mpld3
from flask import Flask, jsonify, request, render_template, send_file, make_response
import requests
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://mongodb:27017')
db = client['web_scraper']
collection = db['data']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    url = request.form['url']
    data_type = request.form.getlist('data_type')
    response = requests.post('http://engine:8000/parse', json={'url': url, 'data_type': data_type})
    data = response.json()
    main_data = {
        'url': data['url'],
        'emails': data.get('emails', []),
        'phone_numbers': data.get('phone_numbers', []),
        'images': data.get('images', []),
        'videos': data.get('videos', []),
        'nips': data.get('nips', []),
        'subpages': data.get('subpages', [])
    }

    collection.insert_one(main_data)
    
    return render_template('index.html', main_data=main_data)

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/stats/data')
def stats_data():
    pipeline = [
        {
            '$group': {
                '_id': '$url',
                'total_emails': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$emails'}, {'$size': '$emails'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.emails'}, {'$size': '$$subpage.emails'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_phone_numbers': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$phone_numbers'}, {'$size': '$phone_numbers'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.phone_numbers'}, {'$size': '$$subpage.phone_numbers'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_images': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$images'}, {'$size': '$images'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.images'}, {'$size': '$$subpage.images'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_videos': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$videos'}, {'$size': '$videos'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.videos'}, {'$size': '$$subpage.videos'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_nips': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$nips'}, {'$size': '$nips'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.nips'}, {'$size': '$$subpage.nips'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_scrapes': {'$sum': 1}
            }
        },
        {
            '$sort': {
                'total_scrapes': -1
            }
        }
    ]
    
    stats = list(collection.aggregate(pipeline))
    
    for stat in stats:
        stat['total_emails'] = stat['total_emails'] // 2
        stat['total_phone_numbers'] = stat['total_phone_numbers'] // 2
        stat['total_images'] = stat['total_images'] // 2
        stat['total_videos'] = stat['total_videos'] // 2
        stat['total_nips'] = stat['total_nips'] // 2
    return jsonify(stats)


def extract_domain(url):
    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if match:
        domain = match.group(1)
        return domain
    return None

@app.route('/stats/plot/png')
def stats_plot_png():
    pipeline = [
        {
            '$group': {
                '_id': '$url',
                'total_emails': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$emails'}, {'$size': '$emails'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.emails'}, {'$size': '$$subpage.emails'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_phone_numbers': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$phone_numbers'}, {'$size': '$phone_numbers'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.phone_numbers'}, {'$size': '$$subpage.phone_numbers'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_images': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$images'}, {'$size': '$images'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.images'}, {'$size': '$$subpage.images'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_videos': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$videos'}, {'$size': '$videos'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.videos'}, {'$size': '$$subpage.videos'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_nips': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$nips'}, {'$size': '$nips'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.nips'}, {'$size': '$$subpage.nips'}, 0]}
                                }
                            }}
                        ]
                    }
                }
            }
        },
        {
            '$sort': {
                'total_images': -1
            }
        }
    ]
    stats = list(collection.aggregate(pipeline))

    for stat in stats:
        stat['total_emails'] = stat['total_emails'] // 2
        stat['total_phone_numbers'] = stat['total_phone_numbers'] // 2
        stat['total_images'] = stat['total_images'] // 2
        stat['total_videos'] = stat['total_videos'] // 2
        stat['total_nips'] = stat['total_nips'] // 2

    domains = []
    emails = []
    phones = []
    images = []
    videos = []
    nips = []

    for stat in stats:
        if stat['_id'] is not None:
            domain = extract_domain(stat['_id'])
            if domain:
                domains.append(domain)
                emails.append(stat['total_emails'])
                phones.append(stat['total_phone_numbers'])
                images.append(stat['total_images'])
                videos.append(stat['total_videos'])
                nips.append(stat['total_nips'])
            else:
                print(f"Could not extract domain from URL: {stat['_id']}")
        else:
            print("Found null URL in stats")

    if domains:
        fig, ax = plt.subplots()
        fig.set_size_inches(19.2, 10.8)

        bar_width = 0.35
        opacity = 0.8

        index = np.arange(len(domains))

        bars_emails = ax.bar(index, emails, bar_width, label='Emails', alpha=opacity, color='b')
        bars_phones = ax.bar(index, phones, bar_width, bottom=emails, label='Phone Numbers', alpha=opacity, color='r')
        bars_images = ax.bar(index, images, bar_width, bottom=np.array(emails) + np.array(phones), label='Images', alpha=opacity, color='g')
        bars_videos = ax.bar(index, videos, bar_width, bottom=np.array(emails) + np.array(phones) + np.array(images), label='Videos', alpha=opacity, color='y')
        bars_nips = ax.bar(index, nips, bar_width, bottom=np.array(emails) + np.array(phones) + np.array(images) + np.array(videos), label='NIPs', alpha=opacity, color='purple')

        ax.set_xlabel('Domains', fontsize=14)
        ax.set_ylabel('Counts', fontsize=14)
        ax.set_title('Scraping Stats', fontsize=18)
        ax.set_xticks(index)
        ax.set_xticklabels(domains, rotation=45, ha='right', fontsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.set_axisbelow(True)

        fig.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        return send_file(buf, mimetype='image/png')
    else:
        return 'No valid websites available for plotting as PNG.'
        
@app.route('/stats/plot/html')
def stats_plot_html():
    pipeline = [
        {
            '$group': {
                '_id': '$url',
                'total_emails': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$emails'}, {'$size': '$emails'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.emails'}, {'$size': '$$subpage.emails'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_phone_numbers': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$phone_numbers'}, {'$size': '$phone_numbers'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.phone_numbers'}, {'$size': '$$subpage.phone_numbers'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_images': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$images'}, {'$size': '$images'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.images'}, {'$size': '$$subpage.images'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_videos': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$videos'}, {'$size': '$videos'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.videos'}, {'$size': '$$subpage.videos'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_nips': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$nips'}, {'$size': '$nips'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.nips'}, {'$size': '$$subpage.nips'}, 0]}
                                }
                            }}
                        ]
                    }
                }
            }
        },
        {
            '$sort': {
                'total_images': -1
            }
        }
    ]

    stats = list(collection.aggregate(pipeline))

    for stat in stats:
        stat['total_emails'] = stat['total_emails'] // 2
        stat['total_phone_numbers'] = stat['total_phone_numbers'] // 2
        stat['total_images'] = stat['total_images'] // 2
        stat['total_videos'] = stat['total_videos'] // 2
        stat['total_nips'] = stat['total_nips'] // 2

    domains = []
    emails = []
    phones = []
    images = []
    videos = []
    nips = []

    for stat in stats:
        if stat['_id'] is not None:
            domain = extract_domain(stat['_id'])
            if domain:
                domains.append(domain)
                emails.append(stat['total_emails'])
                phones.append(stat['total_phone_numbers'])
                images.append(stat['total_images'])
                videos.append(stat['total_videos'])
                nips.append(stat['total_nips'])
            else:
                print(f"Could not extract domain from URL: {stat['_id']}")
        else:
            print("Found null URL in stats")

    if domains:
        fig, ax = plt.subplots()
        fig.set_size_inches(19.2, 10.8)

        width = 0.2
        x = np.arange(len(domains))

        bars_emails = ax.bar(x, emails, width, label='Emails', color='b', alpha=0.7)
        bars_phones = ax.bar(x, phones, width, label='Phone Numbers', color='r', alpha=0.7, bottom=emails)
        bars_images = ax.bar(x, images, width, label='Images', color='g', alpha=0.7, bottom=[i+j for i,j in zip(emails, phones)])
        bars_videos = ax.bar(x, videos, width, label='Videos', color='y', alpha=0.7, bottom=[i+j+k for i,j,k in zip(emails, phones, images)])
        bars_nips = ax.bar(x, nips, width, label='NIPs', color='purple', alpha=0.7, bottom=[i+j+k+l for i,j,k,l in zip(emails, phones, images, videos)])
        
        ax.set_xlabel('Domains')
        ax.set_ylabel('Counts')
        ax.set_title('Scraping Stats')
        ax.legend()

        ax.set_xticks(x)
        ax.set_xticklabels([])

        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)

        for i, domain in enumerate(domains):
            ax.text(i, -0.1, domain, rotation=45, ha='right', fontsize=10)

        tooltip_labels = [f'{domain}\nEmails: {email}\nPhone Numbers: {phone}\nImages: {image}\nVideos: {video}\nNIPs: {nip}'
                          for domain, email, phone, image, video, nip in zip(domains, emails, phones, images, videos, nips)]

        scatter = ax.scatter(x, [0]*len(domains), s=0, color='none')
        tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=tooltip_labels)
        mpld3.plugins.connect(fig, tooltip)

        html = mpld3.fig_to_html(fig)
        plt.close(fig)
        return html
    else:
        return 'No valid websites available for plotting as HTML.'

@app.route('/download/csv')
def download_csv():
    pipeline = [
        {
            '$group': {
                '_id': '$url',
                'total_emails': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$emails'}, {'$size': '$emails'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.emails'}, {'$size': '$$subpage.emails'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_phone_numbers': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$phone_numbers'}, {'$size': '$phone_numbers'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.phone_numbers'}, {'$size': '$$subpage.phone_numbers'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_images': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$images'}, {'$size': '$images'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.images'}, {'$size': '$$subpage.images'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_videos': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$videos'}, {'$size': '$videos'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.videos'}, {'$size': '$$subpage.videos'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_nips': {
                    '$sum': {
                        '$add': [
                            {'$cond': [{'$isArray': '$nips'}, {'$size': '$nips'}, 0]},
                            {'$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$subpages', []]},
                                    'as': 'subpage',
                                    'in': {'$cond': [{'$isArray': '$$subpage.nips'}, {'$size': '$$subpage.nips'}, 0]}
                                }
                            }}
                        ]
                    }
                },
                'total_scrapes': {'$sum': 1}
            }
        },
        {
            '$sort': {
                'total_scrapes': -1
            }
        }
    ]

    stats = list(collection.aggregate(pipeline))

    for stat in stats:
        stat['total_emails'] = stat['total_emails'] // 2
        stat['total_phone_numbers'] = stat['total_phone_numbers'] // 2
        stat['total_images'] = stat['total_images'] // 2
        stat['total_videos'] = stat['total_videos'] // 2
        stat['total_nips'] = stat['total_nips'] // 2

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['URL', 'Total Emails', 'Total Phone Numbers', 'Total Images', 'Total Videos', 'Total NIPs', 'Total Scrapes'])
    for stat in stats:
        cw.writerow([stat['_id'], stat['total_emails'], stat['total_phone_numbers'], stat['total_images'], stat['total_videos'], stat['total_nips'], stat['total_scrapes']])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=scraping_stats.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
