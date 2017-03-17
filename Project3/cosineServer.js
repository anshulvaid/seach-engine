const express = require('express');
const app = express();
const MongoClient = require('mongodb').MongoClient;
const snowball = require('node-snowball');
const sw = require('stopword')
const HashMap = require('hashmap');
var db;
var N = 23555; 
MongoClient.connect("mongodb://localhost:27017/expressengine", (err, database)=>{
    if(err) return console.log(err)
    db = database;
});

// app.set('view engine', 'ejs');

app.get('/', (req, res) =>{
	var headers = {};
    headers["Access-Control-Allow-Origin"] = "*";
    headers["Access-Control-Allow-Methods"] = "POST, GET, PUT, DELETE, OPTIONS";
    headers["Access-Control-Allow-Credentials"] = true;
    headers["Access-Control-Max-Age"] = '86400'; // 24 hours
    headers["Access-Control-Allow-Headers"] = "X-Requested-With, Access-Control-Allow-Origin, X-HTTP-Method-Override, Content-Type, Authorization, Accept";

	console.log(req.query)
	var q = req.query.q.toLowerCase()
	q.replace(/[^a-zA-Z0-9' ]/g, " ");
	var qArr = q.split(" ")
	qArr = sw.removeStopwords(qArr)
	qArr = snowball.stemword(qArr)

	var query ={};
	query["$or"] = [];
	for(var i=0; i < qArr.length; i++){
		query["$or"].push({"token":qArr[i]});
	}
	console.log(query)
	var rankData = new HashMap();
	//var length = new HashMap();
	getPostings(query, function(results){
		// console.log(results);
		for(var i =0; i<results.length; i++){
			var idf_qt = Math.log2(N/parseInt(results[i].doc_frequency));
			for(var j =0; j<results[i].postings.length; j++){
				if(rankData.get(results[i].postings[j].docID) != null){
					(rankData.get(results[i].postings[j].docID)).cosineScore += results[i].postings[j].tf_idf * idf_qt;
				}
				else{
					var value = {cosineScore:results[i].postings[j].tf_idf * idf_qt, pos:results[i].postings[j].position[0]};
					rankData.set(results[i].postings[j].docID, value);
					//length.set(results[i].postings[j].docID, results[i].postings[j].token_count);
				}
				// console.log(results[i].title);
				if(qArr.length <= 4){
					if(results[i].title.indexOf(results[i].postings[j].docID) > -1)
						(rankData.get(results[i].postings[j].docID)).cosineScore += 50;
					if(results[i].url.indexOf(results[i].postings[j].docID) > -1)
						(rankData.get(results[i].postings[j].docID)).cosineScore += 15;
				}
				// for(var k =0; k<results[i].postings[j].zones.length; k++){
				// 	if(results[i].postings[j].zones[k] == "title"){
				// 		(rankData.get(results[i].postings[j].docID)).cosineScore += 50;
				// 	}
				// 	if(results[i].postings[j].zones[k] == "url"){
				// 		(rankData.get(results[i].postings[j].docID)).cosineScore += 25;
				// 	}
				// 	if(results[i].postings[j].zones[k] == "header"){
				// 		(rankData.get(results[i].postings[j].docID)).cosineScore += 5;
				// 	}
				// }
			}
		}

		// rankData.forEach(function(value, key) {
		// 	console.log(key +" => " + value.cosineScore);
		// 	console.log(length.get(key))
		// 	value.cosineScore /= Math.sqrt(length.get(key)); 
		//     rankData.set(key, value)
		// });

		getRankings(rankData, res);
	});
	

	// res.render('results',{
	// 	docs : returnDocs
	// });
	
})

function getPostings(query, callback){
	db.collection('sherlockIndex').find(query).toArray((err, results)=>{
		callback(results);
	})
}

function getDocuments(query, callback){
	db.collection('docIndex').find(query).toArray((err, results)=>{
		callback(results);
	})
}

function getRankings(rankData, res){
	// console.log(rankData)

	
	query = {};
	query["$or"] = [];
	keysSorted = rankData.keys().sort(function(a,b){return (rankData.get(b)).cosineScore-(rankData.get(a)).cosineScore;});
	for(var i=0; i<Math.min(30, keysSorted.length) ; i++){
		query["$or"].push({"docId":keysSorted[i]});
	}
	console.log(query);
	rankData.forEach(function(value, key) {
		console.log(key +" => " + value.cosineScore);
	});

	returnDocs = []
	getDocuments(query, function(results){
		for(var i =0; i< results.length; i++){
			var index = keysSorted.indexOf(results[i].docId)
			var titleWithBody = results[i].text;
			var textArr = titleWithBody.split(" ");
			var pos = (rankData.get(results[i].docId)).pos;
			var start = 0, end = textArr.length-1
			if((pos-10) >= 0){
				start = pos-10;
			}
			if((pos+10) < textArr.length){
				end =pos+10;
			}
			textArr = textArr.slice(start, end);
			results[i].text = textArr.join(" ");
			// returnDocs.push(results[i]);
			returnDocs[index] = results[i];
		}
		res.setHeader("Access-Control-Allow-Origin", "*");
		res.send(JSON.stringify(returnDocs));
	});
}

app.listen(3000, function(){
	console.log('listening to 3000');
})

