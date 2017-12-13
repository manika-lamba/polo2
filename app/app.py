import os, sys
from flask import Flask, render_template
from polo2 import PoloDb, PoloConfig

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(base_dir)
from elements import Elements

app = Flask(__name__)
app.config.from_object('config')

projects_dir = app.config['PROJECTS_DIR']
data = {} # Use to store variables to pass to templates
data['main_menu'] = [
    ('/projects', 'Projects'),
]

@app.route("/")
@app.route("/projects")
def hello():
    data['page_title'] = 'Project List'
    data['projects'] = [dir for dir in os.listdir(projects_dir) if os.path.isfile(get_project_config_file(dir))]
    return render_template('home.html', **data)

@app.route('/test')
def test():
    return render_template('test.html')

@app.route("/projects/<slug>")
@app.route("/projects/<slug>/<trial>")
def projects(slug, trial='trial1'):
    cfg = get_project_config(slug)
    els = Elements(cfg, trial)
    data['ini'] = cfg.ini['DEFAULT']
    data['trials'] = cfg.get_trial_names()
    data['slug'] = slug
    data['trial'] = trial
    data['page_title'] = 'Project {}, Trial {}'.format(slug, trial)
    data['doc_count'] = els.get_doc_count()
    data['topic_count'] = els.get_topic_count()
    data['topic_list'] = els.get_topic_list()
    data['topics'] = els.model.get_table('topic', set_index=True)
    data['test'] = els.test()
    return render_template("project.html", **data)

@app.route("/projects/<slug>/<trial>/topic_label_heatmap")
def topic_label_heatmap(slug, trial='trial1'):
    cfg = get_project_config(slug)
    els = Elements(cfg, trial)
    data['ini'] = cfg.ini['DEFAULT']
    data['trials'] = cfg.get_trial_names()
    data['slug'] = slug
    data['trial'] = trial
    data['page_title'] = 'Project {}, Trial {}, Topic-Label Heatmap'.format(slug, trial)
    data['dtm'] = els.get_topic_label_matrix()
    return render_template("topic_label_heatmap.html", **data)

# Helpers -- Consider moving to module
def get_project_config_file(slug):
    return '{}/{}/config.ini'.format(projects_dir, slug)

def get_project_config(slug):
    pcfg_file = get_project_config_file(slug) #'{}/{}/config.ini'.format(projects_dir, slug)
    pcfg = PoloConfig(pcfg_file)
    return pcfg

def get_corpus_db(slug):
    pcfg = get_project_config(slug)
    corpus_db_file = pcfg.generate_corpus_db_file_path()
    corpus = PoloDb(corpus_db_file)
    return corpus

def get_model_db(slug, trial):
    pcfg = get_project_config(slug)
    model_db_file = pcfg.generate_model_db_file_path(trial)
    model = PoloDb(model_db_file)
    return model

if __name__ == '__main__':
    app.run(debug=True)