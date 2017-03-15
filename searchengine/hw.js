var http = require('http'), 
	url = require('url'),
	qs = require('querystring'),
	MongoClient = require("mongodb").MongoClient,
	snowball = require('node-snowball'),
	databaseURL = "mongodb://localhost:27017/search_engine",
	indexCollection = "Index",
	docCollection = "docIndex",
	assert = require('assert'),
	HashMap = require('hashmap');

console.log("active")


var server = http.createServer(function onRequest(request, response){
	    // add needed headers
    var headers = {};
    headers["Access-Control-Allow-Origin"] = "*";
    headers["Access-Control-Allow-Methods"] = "POST, GET, PUT, DELETE, OPTIONS";
    headers["Access-Control-Allow-Credentials"] = true;
    headers["Access-Control-Max-Age"] = '86400'; // 24 hours
    headers["Access-Control-Allow-Headers"] = "X-Requested-With, Access-Control-Allow-Origin, X-HTTP-Method-Override, Content-Type, Authorization, Accept";
	    // respond to the request
	    

	var urlParts = url.parse(request.url);
	var querystr = qs.parse(urlParts.query)
	console.log(querystr.q)
	var q = querystr.q
	var qArr = q.split(" ")
	qArr = snowball.stemword(qArr)
	console.log(qArr)
	// db.getCollection('Index').find({$or: [{token:"crista"}, {token:"lope"}]}).pretty()

	var query ={};
	query["$or"] = [];
	for(var i=0; i < qArr.length; i++){
		query["$or"].push({"token":qArr[i]});
	}
	console.log(query)

	var map = new HashMap();
	var connection = MongoClient.connect(databaseURL, function(err, db){
		assert.equal(null, err);
		var cursor = db.collection(indexCollection).find(query);
			
		cursor.each(function(err, doc){
			if(!err && doc){
				for(var i=0; i<doc.postings.length; i++){
					if(map.get(doc.postings[i].docID) != null){
						(map.get(doc.postings[i].docID)).tf_idf += doc.postings[i].tf_idf;
					}
					else{
						var value = {tf_idf:doc.postings[i].tf_idf, pos:doc.postings[i].position[0]};
						map.set(doc.postings[i].docID, value)
					}
				}
			}else{
				query = {};
				query["$or"] = [];
				keysSorted = map.keys().sort(function(a,b){return (map.get(b)).tf_idf-(map.get(a)).tf_idf;});
				for(var i=0; i<keysSorted.length; i++){
					query["$or"].push({"docId":keysSorted[i]});
				}
				var cur = db.collection(docCollection).find(query);
				docs = []
				cur.each(function(e, doc2){
					if(!e && doc2){
						var titleWithBody = doc2.text 
						// titleWithBody = titleWithBody.replace(/[^0-9a-z']\s/gi, '')
						var textArr = titleWithBody.split(" ");
						var pos = (map.get(doc2.docId)).pos;
						var start = 0, end = textArr.length-1
						if((pos-10) >= 0){
							start = pos-10;
						}
						if((pos+10) < textArr.length){
							end =pos+10;
						}
						textArr = textArr.slice(start, end);
						doc2.text = textArr.join(" ");
						docs.push(doc2);
					}else{
						db.close();
						done();
						response.writeHead(200, headers);
						response.end(JSON.stringify(docs), 'utf-8');
					}
				});
				return;
			}
		});
	});
		
}).listen(3300);

function done(){
	console.log("done")
}	 