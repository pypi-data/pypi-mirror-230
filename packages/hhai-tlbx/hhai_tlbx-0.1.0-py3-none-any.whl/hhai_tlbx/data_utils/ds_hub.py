from .ds_utils import (
    DataSource,
    Parse_inst,
    get_src_path
)

def get_dataset_dict(ds_name):
    import rapidjson 
    if ds_name == 'city_scape':
        im_ds_src = DataSource(
            path='leftImg8bit/train',
            name_lst=['*'],
            ext_lst=['png'],
            field=['img'],
            make_label=None
        )
        lab_ds_src = DataSource(
            path='gtFine/train',
            name_lst=['*_edgeMaps', '*_instanceIds', '*_labelIds'],
            ext_lst=['png'],  # short-syntax for ['png', 'png', 'png'] !
            field=['edge', 'inst', 'lbid'],
            make_label=None
        )
        # implement paired mode !
        src_path_dct = get_src_path(
            rt_dir="/data1/dataset/Cityscapes",
            ds_src_lst=[im_ds_src, lab_ds_src],
            sort_kwargs={'reverse':True},
            ret_dict=False
        )

        return src_path_dct

    elif (ds_name == 'celeba_hq') or (ds_name == 'alps_seasons'):
        # func used to make the label
        def im_fd_label(all_dct):
            lab_dct = defaultdict(list)
            for path in all_dct['img']:
                fld_name = Path(path).parent.stem
                lab_dct['label'].append(fld_name)
            return lab_dct

        # implement image folder mode by glb_func
        im_ds_src = DataSource(
            path='train',
            name_lst=['*'],
            ext_lst=['jpg'],
            field=['img'],
            make_label=im_fd_label
        )
        all_src_path = get_src_path(
            rt_dir=f'/data1/dataset/{ds}',
            ds_src_lst=[im_ds_src],
            ret_dict=False
        )

        for img, lab in all_src_path:
            breakpoint()

    elif ds_name == 'WeatherGAN':
        # func used to make the label
        def filename_label(all_dct):
            lab_dct = defaultdict(list)
            for path in all_dct['img']:
                wea_cond = Path(path).stem.split('_')[0]
                lab_dct['label'].append(wea_cond)
            return lab_dct

        # weatherGAN ds is special, 
        #   you can even specific name_lst to partially load the specific weather imgs.
        im_ds_src = DataSource(
            path='train_images',
            name_lst=['*'],
            ext_lst=['jpg'],
            field=['img'],
            make_label=filename_label
        )
        all_src_path = get_src_path(
            rt_dir=f'/data1/dataset/{ds}',
            ds_src_lst=[im_ds_src],
            ret_dict=False
        )

        for img, lab in all_src_path:
            breakpoint()

    elif ds_name == 'COCO':
        def js_file_handler(js_dct):
            import itertools

            def ld_ann_id(imgIds, imgToAnns):
                lists = [imgToAnns[imgId] for imgId in [imgIds] if imgId in imgToAnns]
                anns = list(itertools.chain.from_iterable(lists))
                ids = [ann['id'] for ann in anns]
                return ids

            # create_idx : 
            anns, cats, imgs = {}, {}, {}
            imgToAnns,catToImgs = defaultdict(list),defaultdict(list)
            if 'annotations' in js_dct:
                for ann in js_dct['annotations']:
                    imgToAnns[ann['image_id']].append(ann)
                    anns[ann['id']] = ann

            if 'images' in js_dct:
                for img in js_dct['images']:
                    imgs[img['id']] = img

            if 'categories' in js_dct:
                for cat in js_dct['categories']:
                    cats[cat['id']] = cat

            if 'annotations' in js_dct and 'categories' in js_dct:
                for ann in js_dct['annotations']:
                    catToImgs[ann['category_id']].append(ann['image_id'])
            # load imgs
            dct = defaultdict(list)
            for im_id in sorted(imgs.keys()):
                dct['path'].append( imgs[im_id]["file_name"] )
                tmp = [ anns[ann_id] for ann_id in ld_ann_id(im_id, imgToAnns) ]
                dct['ann'].append(tmp)
            return dct

        par_inst = Parse_inst('json', js_file_handler, js_qry_dct={})
        # implement image folder mode by glb_func
        js_ds_src = DataSource(
            path='annotations',
            name_lst=['instances_train2017'],
            ext_lst=['json'],
            field=['_js']
        )
        #  # {'json':(js_file_handler, qry_dct)},  # parser_inst
        all_src_path = get_src_path(
            rt_dir='/data1/dataset/COCO/coco/',
            ds_src_lst=[js_ds_src],
            parse_lst=[par_inst],
            sort_path=False,
            ret_dict=False
        )

        for im, ann in all_src_path:
            breakpoint()

    elif ds_name == 'bdd': # bdd dataset, json-based structure !!
          # However, we still suggest you can directly write a json file parser, it will much fast!
        # field : query_string
        js_qry_dct = {
            'wea_cond' : "attributes.weather",
            'time' : "attributes.timeofday",
            'name' : "name"
        }
        # func used to handle with json file instance's
        def js_file_handler(tuple_zip):
            # you see! even js file handler is massive!!
            # get_src_path function still allow you to do it in flexible callbk ~
            _exclude_wea_cond = [
                'foggy',
                'partly cloudy',
                'undefined'
            ]
            _exclude__time = [
                'undefined',
                'night'
            ]
            _weather2id = {
                'rainy':0, 
                'snowy':1,
                'clear':2,
                'overcast':3,
                'foggy':4,
                'partly cloudy': 5,
                'undefined': 6
            }
            im_dict = {}
            ds_path_prefix = Path("/data1/dataset/bdd100k/images/100k/train/")
            # quite flexible for query args in json
            for wea_cond, time, name in tuple_zip:
                # weather condition in exclude
                if (wea_cond in _exclude_wea_cond) or (time in _exclude__time):
                    continue
                if not (wea_cond in im_dict.keys()):
                    im_dict[wea_cond] = []
                
                im_path = str(ds_path_prefix / name)
                im_dict[wea_cond].append(im_path)

            fnames, fnames2, labels = [], [], []
            for wea_cond in im_dict.keys():
                fnames.extend(im_dict[wea_cond])
                fnames2.extend(im_dict[wea_cond][1:]+im_dict[wea_cond][:1])
                idx = _weather2id[wea_cond]
                size = len(im_dict[wea_cond])
                labels.extend([idx] * size)

            return {'fn_1':fnames, 'fn_2':fnames2, 'lab':labels}
        # switch to faster json-loader backend!!
        par_inst = Parse_inst('json', rapidjson.load, js_file_handler, js_qry_dct)

        # implement image folder mode by glb_func
        js_ds_src = DataSource(
            path='labels',
            name_lst=['bdd100k_labels_images_train'],
            ext_lst=['json'],
            field=['_js']
        )
        #  # {'json':(js_file_handler, qry_dct)},  # parser_inst
        all_src_path = get_src_path(
            rt_dir='/data1/dataset/bdd100k',
            ds_src_lst=[js_ds_src],
            parse_lst=[par_inst],
            sort_path=False,
            ret_dict=False
        )

        for fname, fname2, label in all_src_path:
            breakpoint()