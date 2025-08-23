import traceback
from app import app, find_model, model_label

with app.app_context():
    def try_render(name, ctx):
        try:
            # create a test request context so url_for() and request-specific globals work
            with app.test_request_context('/'):
                t = app.jinja_env.get_template(name)
                out = t.render(**ctx)
                print(f"TEMPLATE {name} OK, length={len(out)}")
        except Exception:
            print(f"TEMPLATE {name} ERROR:\n")
            traceback.print_exc()

    models = find_model()
    det_models = [(m, model_label(m)) for m in models]
    seg_models = [(m, model_label(m)) for m in models]
    last = {'task':'detection','det_model':'','seg_model':'','pad':10,'multi_leaf':''}

    # dataset context
    import os
    base = os.path.join('static','dataset_samples')
    samples = {}
    full_lists = {}
    for subset in ('train','valid','test'):
        folder = os.path.join(base, subset)
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg','.jpeg','.png'))]
            files_sorted = sorted(files)
            samples[subset] = files_sorted[:6]
            full_lists[subset] = files_sorted
        else:
            samples[subset]=[]; full_lists[subset]=[]

    def infer_class(name):
        lname = name.lower()
        if 'frog' in lname: return 'frog-eye-leaf-spot'
        if 'rust' in lname: return 'rust'
        if 'healthy' in lname: return 'healthy'
        return 'unknown'
    classes = {s:{f:infer_class(f) for f in fl} for s,fl in full_lists.items()}

    ctx_upload = {'det_models':det_models,'seg_models':seg_models,'last':last,'uploaded':'','result':None}
    ctx_dataset = {'samples':samples,'full_lists':full_lists,'classes':classes}
    ctx_dashboard = {'examples':{'nano':[],'small':[],'medium':[]}, 'models':det_models}
    ctx_project = {'graphs':[]}

    try_render('upload.html', ctx_upload)
    try_render('dataset.html', ctx_dataset)
    try_render('dashboard.html', ctx_dashboard)
    try_render('project.html', ctx_project)
