//var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
//var axios = require("../../../user_managed_content/static/js/axios.min.js");

function get_server_uri(uri) {
    //return "http://localhost:5000" + uri
    return uri
}


function error_processor(class_name, method_name, err) {
    var ret_data = null
    if (err.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.log("response headers:");
      console.log("=================");
      console.log(err.response.headers);
      console.log("");
      console.log("response payload: ");
      console.log("=================");
      console.log(err.response.data);
      console.log("");
      console.log("status:" + err.response.status);
      console.log("");
      console.log("");

      ret_data = class_name + "." + method_name + "." + "server" + "." + err.response.data.error_code
    
    } else if (err.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.log(err.request);
      ret_data = class_name + "." + method_name + "." + "client" + "." + err.constructor.name

    } else {
        console.log("SetupError Type: " + err.constructor.name)
        console.log("SetupError detail: ")
        console.log("==================")
        console.log(err)
        console.log("");
        console.log("");
          // Something happened in setting up the request that triggered an Error
        ret_data = class_name + "." + method_name + "." + "client" + "." + err.constructor.name
    }

    return ret_data
}


//const { default: axios } = require("axios")

TYPE_UNKNOWN = 10
TYPE_FOLDER = 0
TYPE_HTML_DOCUMENT = 1
TYPE_TEXT_DOCUMENT = 2
TYPE_BINARY_DOCUMENT = 3


class FolderItem {
    constructor(is_folder, name, parent_folder) {
        this.is_folder      = is_folder
        this.parent_folder  = parent_folder
        this.is_root_folder = false
        this.name           = name

        if (this.parent_folder) {
            this.uri  = this.parent_folder.uri + "/" + name
        }
        var key_prefix
        
        if (this.is_folder) {
            key_prefix = "folder_"
        } else {
            key_prefix = "file_"
        }

        this.lookup_key = key_prefix + name
    }

    async rename(name, onConfirm, onConfirmError) {
        var payload = {
            "from_uri" : this.uri,
            "to_uri" : this.parent_folder.uri + "/" + name,
            "is_folder" : this.is_folder
        }
        var move_uri = "/arches/content/manage/api/resource/move/" + this.get_root_folder().name
        await axios.post(get_server_uri(move_uri), payload).then( response => {
            this.name = name

            var key_prefix
    
            if (this.is_folder) {
                key_prefix = "folder_"
            } else {
                key_prefix = "file_"
            }
    
            this.lookup_key = key_prefix + name

            this.uri = this.parent_folder.uri + "/" + name

            if (onConfirm) {
                onConfirm()
            }

        }).catch((err) => {

            var ret_code = error_processor(this.constructor.name, "rename", err)
            
            if (onConfirmError) {
                onConfirmError(ret_code)
            }
        })
    }


    get_root_folder() {
        var current_parent = null
        if (this.is_root_folder) {
            current_parent = this
        } else {
            if ( this.parent_folder == null ) {
                throw Error("Folder item " + this.key + " has no parent defined")
            }
            current_parent = this.parent_folder
            while (!current_parent.is_root_folder) {
                current_parent = current_parent.parent_folder
            }
        }
        return current_parent
    }

    async move(new_parent_folder, onConfirm, onConfirmError) {
        var payload = {
            "from_uri" : this.uri,
            "to_uri" : new_parent_folder.uri + "/" + this.name,
            "is_folder" : this.is_folder
        }

        var move_uri = "/arches/content/manage/api/resource/move/" + this.get_root_folder().name
        await axios.post(get_server_uri(move_uri), payload).then( response => {
            var old_parent_folder = this.parent_folder
            old_parent_folder.remove_child_node(this)
            new_parent_folder.add_child_node(this)
            if (onConfirm) {
                onConfirm()
            }
        }).catch((err) => {

            var ret_code = error_processor(this.constructor.name, "move", err)
            
            if (onConfirmError) {
                onConfirmError(ret_code)
            }
        })
    }

    async delete(onConfirm, onConfirmError) {
        var del_uri = null
        if (this.is_folder) {
            del_uri = get_server_uri("/arches/content/manage/api/folder" + this.uri)
        }
        axios.delete(del_uri).then(() => {
            onConfirm()
        }).catch((err) => {
            var ret_code = error_processor(this.constructor.name, "move", err)
            
            if (onConfirmError) {
                onConfirmError(ret_code)
            }
        })
    }
}



detectable_types = {
    "html" : TYPE_HTML_DOCUMENT,
    "htm" : TYPE_TEXT_DOCUMENT,
    "css" : TYPE_TEXT_DOCUMENT,
    "json" : TYPE_TEXT_DOCUMENT,
    "yaml" : TYPE_TEXT_DOCUMENT,
    "yml" : TYPE_TEXT_DOCUMENT,
    "js" : TYPE_TEXT_DOCUMENT,
    "mjs" : TYPE_TEXT_DOCUMENT,
    "csv" : TYPE_TEXT_DOCUMENT,
    "txt" : TYPE_TEXT_DOCUMENT,
    "xml" : TYPE_TEXT_DOCUMENT
}


function get_extension(name) {
    ext = null

    var re = /(?:\.([^.]+))?$/;

    var ext = re.exec(name)[1];   // "txt"

    if (ext == undefined) {
        ext = ""
        //throw Error("no extnsion found in file name [" + name + "]")
    }

    return ext
}


function get_type(name) {
    ret_vaue = null

    ext = get_extension(name).toLowerCase()


    if (detectable_types[ext] === undefined) {
        ret_value = TYPE_BINARY_DOCUMENT
    } else {
        ret_value = detectable_types[ext]
    }

    return ret_value
}



class BaseFolder extends FolderItem {
    constructor(name, parent_folder) {
        super(true, name, parent_folder)
        this.children       = null
        this.is_root_folder = null
        this.type           = TYPE_FOLDER
        //this.uri            = null
    }


    find_folder_item_by_key(lookup_key) {
        var ret_value = null
        if (this.children) {
            for (i=0; i<this.children.length; i++) {
                if (this.children[i].lookup_key == lookup_key) {
                    ret_value = this.children[i]
                    break
                } 
            }
        }
        return ret_value
    }


    find_folder_item_index(name, is_folder) {
        var ret_value = null
        if (this.children) {
            for (i=0; i<this.children.length; i++) {
                if (this.children[i].name == name && this.children[i].is_folder == is_folder) {
                    ret_value = i
                    break
                } 
            }
        }
        return ret_value
    }


    find_folder_item(name, is_folder) {
        var ret_value = null
        var index = this.find_folder_item_index(name, is_folder)
        if (index != null) {
            ret_value = this.children[index]
        }
        return ret_value
    }


    add_child_node(child_node) {
        if (this.children) {
            this.children[this.children.length] = child_node
            child_node.parent_folder = this
            this.adjust_uris_after_move(child_node)
            this.sort_children()
        }
    }


    adjust_uris_after_move(child_node) {
        child_node.uri  = child_node.parent_folder.uri + "/" + child_node.name

        if (child_node.is_folder) {
            if (child_node.children) {
                for (var i=0; i<child_node.children.length; i++) {
                    this.adjust_uris_after_move(child_node.children[i])
                }
            }
        }
    }

    remove_child_node(child_node) {
        var removed_child = null
        for (var i=0; i<this.children.length; i++) {
            if (child_node === this.children[i]) {
                removed_child = this.children[i]
                this.children.splice(i, 1)
            }
        }

        if (removed_child == null) {
            throw Error("Could not find child node in parent folder, parent folder uri:[" + this.uri + "], name:[" + child_node.name + "], is folder flag:[" + child_node.is_folder + "]")
        }
    }


    async load_children(onConfirm, onConfirmError) {
        var server_uri = get_server_uri("/arches/content/manage/api/folder" + this.uri)
        await axios.get(server_uri).then( response => {
            //this.children = build_list(response, this)
            if (this.children == null) {
                this.children = []
            }
            var temp_children = build_list(response, this)

            // remove children not in dest list
            var i=0
            while (i<this.children.length) {
                if (! this.folder_item_in_children(this.children[i], temp_children)) {
                    this.children.splice(i, 1)
                } else {
                    i++
                }
            }

            for (i=0; i<temp_children.length; i++) {
                if (! this.folder_item_in_children(temp_children[i], this.children)) {
                    this.children[this.children.length] = temp_children[i]
                }
            }

            this.sort_children()

            if (onConfirm) {
                onConfirm()
            }
        }).catch( err => {
            var ret_code = error_processor(this.constructor.name, "load_children", err)
            
            if (onConfirmError) {
                onConfirmError(ret_code)
            }
        })
    }

    folder_item_in_children(folder_item, child_list) {
        ret_value = false
        for (var i=0; i<child_list.length; i++) {
            if (child_list[i].uri == folder_item.uri) {
                ret_value = true
                break
            }
        }
        return ret_value
    }

    async create_child_folder(name, onConfirm, onConfirmError) {
        var error_found = false
        await axios.post(get_server_uri("/arches/content/manage/api/folder" + this.uri + "/" + name)).then(response => {
        }).catch(err => {
            var ret_code = error_processor(this.constructor.name, "create_child_folder", err)
            
            if (onConfirmError) {
                onConfirmError(ret_code)
            }

            error_found = true
        })

        if (!error_found) {
            if (!this.children) {
                await this.load_children(onConfirm, onConfirmError)
            } else {
                var new_child_folder = new ChildFolder(name, this)
                this.children[this.children.length] = new_child_folder
                this.sort_children()
                if (onConfirm) {
                    onConfirm()
                }
            }
        }
    }

    sort_children() {
        this.children.sort(compare_items)
    }


    async create_file(name, onError) {
            file_header = FileHeader(name, this)
    }

}


function build_list(response, parent_folder) {
    var data            = response.data
    var child_folders   = data.child_folders
    var files           = data.files
    var ret_children    = []

    for (i=0; i<child_folders.length; i++) {
        folder_name = child_folders[i]
        var cf = new ChildFolder(folder_name, parent_folder)
        ret_children[ret_children.length] = cf
    }

    for (i=0; i<files.length; i++) {
        resource_header = files[i]
        file_type = get_type(resource_header.resource_id)
        var fh = null
        if (file_type == TYPE_TEXT_DOCUMENT) {
            fh = new TextDocument(resource_header.resource_id, parent_folder)
        } else if (file_type == TYPE_HTML_DOCUMENT) {
            fh = new EHTMLDocument(resource_header.resource_id, parent_folder)
        } else {
            fh = new BinaryDocument(resource_header.resource_id, parent_folder)
        }

        ret_children[ret_children.length] = fh 
    }

    return ret_children
  }


function compare_items(i1, i2) {
    var ret_value = 0
    if (i1.is_folder == i2.is_folder) {
      if (i1.name < i2.name) {
        ret_value = -1
      } else if (i1.name > i2.name) {
        ret_value = 1
      } else {
        ret_value = 0
      }
    } else if (i1.is_folder > i2.is_folder) {
      ret_value = -1
    } else {
      ret_value = 1
    }
    return ret_value
  }



class RootFolder extends BaseFolder{
    constructor(base_uri) {

        var segs = base_uri.split("/")
        var folder_name

        if (segs[0] != "") {
            throw Error("Base URL must be preceeded by a /")
        }
        if (segs[segs.length-1] == "") {
            folder_name = segs[segs.length-2]
        } else {
            folder_name = segs[segs.length-1]
        }

        super(folder_name, null)

        this.is_root_folder = true
        this.base_uri = base_uri
        this.uri = this.base_uri
    }

    find_item_by_uri(uri, is_folder) {
        var working_uri = uri
        if (!uri.startsWith(this.base_uri)) {
            throw Error("Provided URI:[" + uri + "] does not start with root folder's base URI:[" + this.base_uri + "]")
        } else {
            working_uri = working_uri.substring(this.base_uri.length, working_uri.length)
        }

        var segs = working_uri.split("/")
        if (segs[segs.length-1] == "") {
            segs.splice(segs.length-1, 1)
        }
        segs.splice(0, 1)

        var working_folder = this
        var i
        for (i=0; i<segs.length-1; i++) {
            var previous_working_folder = working_folder
            working_folder = working_folder.find_folder_item(segs[i], true)
            if (!working_folder) {
                throw Error("Cound not find child folder:[" + segs[i] + "] in parent folder:[" + previous_working_folder.uri + "]")
            }
        }

        var item = working_folder.find_folder_item(segs[segs.length-1], is_folder)

        return item
    }

    async rename(name, onConfirm, onConfirmError) {
        throw Error("rename is not permitted on a root folder")
    }

    async move(new_parent_folder, onConfirm, onConfirmError) {
        throw Error("move is not permitted on a root folder")
    }

    async delete(onConfirm, onConfirmError) {
        throw Error("delete is not permitted on a root folder")
    }
}

function clone(item) {
    if (!item) { return item; } // null, undefined values check

    var types = [ Number, String, Boolean ], 
        result;

    // normalizing primitives if someone did new String('aaa'), or new Number('444');
    types.forEach(function(type) {
        if (item instanceof type) {
            result = type( item );
        }
    });

    if (typeof result == "undefined") {
        if (Object.prototype.toString.call( item ) === "[object Array]") {
            result = [];
            item.forEach(function(child, index, array) { 
                result[index] = clone( child );
            });
        } else if (typeof item == "object") {
            // testing that this is DOM
            if (item.nodeType && typeof item.cloneNode == "function") {
                result = item.cloneNode( true );    
            } else if (!item.prototype) { // check that this is a literal
                if (item instanceof Date) {
                    result = new Date(item);
                } else {
                    // it is an object literal
                    result = {};
                    for (var i in item) {
                        result[i] = clone( item[i] );
                    }
                }
            } else {
                // depending what you would like here,
                // just keep the reference, or create new object
                if (false && item.constructor) {
                    // would not advice to do that, reason? Read below
                    result = new item.constructor();
                } else {
                    result = item;
                }
            }
        } else {
            result = item;
        }
    }

    return result;
}

RemoteObjectMixin = {
    build_remote_uri(base_uri, id) {
        if ((!this._remote_uri) || (id != this._saved_id)) {
            var separator = ""
            if (!id.startsWith("/")) {
                separator = "/"
            }
            this._remote_uri = get_server_uri(base_uri) + separator + id    
        }
        
        this._saved_id = id

        return this._remote_uri
    },
    async _create(onConfirm, onConfirmError) {
        payload = this.build_payload()

        axios.post(this.get_remote_uri(), payload).then(response => {
            if (onConfirm) { 
                this.payload = payload
                onConfirm()
            }
        }).catch(err => {
            return this.process_error("create", err, onConfirmError)
        })
    },
    async _read(onConfirm, onConfirmError) {
        axios.get(this.get_remote_uri()).then(response => {
            this.load_from_payload(response.data)
            this.payload = clone(response.data)

            if (onConfirm) {
                onConfirm()
            }
        }).catch(err => {
            return this.process_error("read", err, onConfirmError)
        })
    },
    async _update(onConfirm, onConfirmError) {
        var payload = this.build_payload()
        axios.put(this.get_remote_uri(), payload).then(response => {
            this.payload = clone(payload)
            if (onConfirm) {
                onConfirm()
            }
        }).catch(err => {
            return this.process_error("update", err, onConfirmError)
        })
    },
    async _delete(onConfirm, onConfirmError) {
        axios.delete(this.get_remote_uri()).then(response => {
            if (onConfirm) {
                onConfirm()
            }
        }).catch(err => {
            return this.process_error("delete", err, onConfirmError)
        })        
    },
    process_error(method_name, err, onConfirmError) {
        var ret_code = error_processor(this.constructor.name, method_name, err)
            
        if (onConfirmError) {
            onConfirmError(ret_code)
        }

        return ret_code
    },
    changed() {
        var ret_value = false

        if (this.payload) {
            var keys = Object.keys(this.payload)

            for (var i=0; i<keys.length; i++) {
                var key = keys[i]
                if (JSON.stringify(this[key]) != JSON.stringify(this.payload[key])) {
                    ret_value = true
                    break
                }
            }
        }
        return ret_value
    }
}



class ResourceHeader {
    constructor(uri, mimetype, resource_id, render_type) {
        this.uri = uri
        this.mimetype = mimetype
        this.resource_id = resource_id
        this.render_type = render_type
    }
}



class EHTMLMetaData {
    constructor() {
        this.layout=null
        this.title=null
        this.keywords=null
        this.description=null
        this.suppress_inheritance=null
        this.extended_attributes=null
        this.scripts=[]
        this.aux_content_items=[]
        this.links=[]
    }
}



class FileHeader extends FolderItem {
    constructor(name, parent_folder) {
        super(false, name, parent_folder)

        this.parent_folder = parent_folder
        this.type = get_type(name)

    }
}



class Document extends FileHeader {
    constructor(name, parent_folder) {
        super(name, parent_folder)
        this.uri = parent_folder.uri + "/" + name        
    }
    get_remote_uri() {
        return this.build_remote_uri("/arches/content/manage/api/document", this.uri)
    }

    init() {

    }

    load_from_payload() {

    }

    build_payload() {
        
    }

    create(onConfirm, onConfirmError) {
        this._create(
            () => {
                this.parent_folder.add_child_node(this)
                onConfirm()
            }
            , 
            onConfirmError
        )
    }

    read(onConfirm, onConfirmError) {
        this._read(onConfirm, onConfirmError)
    }

    update(onConfirm, onConfirmError) {
        this._update(onConfirm, onConfirmError)
    }

    delete(onConfirm, onConfirmError) {
        this._delete(
            () => {
                this.parent_folder.remove_child_node(this)
                onConfirm()
            }
            ,
            onConfirmError
        )
    }
}

Object.assign(Document.prototype, RemoteObjectMixin);



class TextDocument extends Document {
    constructor(name, parent_folder) {
        super(name, parent_folder)
        this.init()
    }

    build_payload() {
        return {"text" : this.text}
    }

    load_from_payload(payload) {
        this.last_modified_date = payload.last_modified_date
        this.text = payload.text
    }

    init() {
        this.text = ""
    }
}



class EHTMLDocument extends Document {
    constructor(name, parent_folder) {
        super(name, parent_folder)
        this.init()
    }

    build_payload() {
        return {
            "text" : this.text,
            "metadata" : this.metadata
        }
    }

    load_from_payload(payload) {
        this.last_modified_date = payload.last_modified_date
        this.text = payload.text
        this.metadata = payload.metadata
    }

    init() {
        this.text=""
        this.metadata=  {
            "layout":"",
            "title":"",
            "keywords":"",
            "description":"",
            "suppress_inheritance":false,
            "extended_attributes":{},
            "scripts" : [],
            "aux_content_refs" : [],
            "links" : []
        }
    }
}


class BinaryDocument extends Document {
    constructor(name, parent_folder) {
        super(name, parent_folder)
        this.init()
    }

    build_payload() {
    }

    load_from_payload(payload) {
        this.last_modified_date = payload.last_modified_date
        this.size = payload.size
    }

    init() {
        this.last_modified_date = ""
        this.size = ""
    }

    update() {
    }

    async _create(onConfirm, onConfirmError) {
        if (onConfirm) { 
            onConfirm()
        }
    }

}



class ChildFolder extends BaseFolder {
    constructor(name, parent_folder) {
        super(name, parent_folder)
        this.is_root_folder = false
    }

    async delete(onConfirm, onConfirmError) {
        super.delete(
            () => {
                this.parent_folder.remove_child_node(this)
                onConfirm()
            },
            onConfirmError
        );
    }
}
