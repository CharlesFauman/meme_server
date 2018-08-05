const socket = io.connect();

function setup() {
	createCanvas(800, 500);

	input = createInput();
	input.size(500, 50);
	//input.style({"word-wrap": "break-word"});

	submit_button = createButton('submit');
	submit_button.mousePressed(request_labels); 

	meme_names = [
	'Condescending Wonka',
	 'Futurama Fry',
	 'Most Interesting Man',
	 'First World Problems',
	 'Grumpy Cat',
	 'What If I Told You',
	 'Forever Alone',
	 'Conspiracy Keanu',
	 'Kermit Drinking Tea',
	 'Trollface',
	 'Insanity Wolf',
	 'Yo Dawg',
	 'Disaster Girl',
	 'Skeptical 3rd World Kid',
	 'Joseph Ducreux',
	 'Slowpoke',
	 'Dr Evil Meme',
	 'Joker Mind Loss',
	 'Stoner Stanley',
	 'Mr Bean',
	 'Good Guy Greg',
	 'Success Kid',
	 'Bad Luck Brian',
	 'Y U No',
	 'One Does Not Simply',
	 'Scumbag Steve',
	 'Philosoraptor',
	 'Batman Slap Robin',
	 'Drunk Baby',
	 'Correction Guy',
	 'Sudden Realization Ralph',
	 'Spongebob Imagination',
	 'Southpark Bad Time',
	 'Chemistry Cat',
	 'Captain Picard',
	 'Doge',
	 'Awkward Situation Seal',
	 'Unpopular Opinion Puffin',
	 'Confession Bear',
	 'That Would Be Great'
	];

	meme_images = {}
	for(var i = 0; i < meme_names.length; ++i){
		meme_images[meme_names[i]] = loadImage("meme_images/" + meme_names[i] + ".jpg");
	}

	meme_scores = []
	for(var i = 0; i < meme_names.length; ++i){
		meme_scores.push([meme_names[i], 0]);
	}
}

function draw(){
	background(0)
	for(var i = 0; i < meme_names.length; ++i){
		image(meme_images[meme_scores[i][0]], (i%8)*100, floor(i/8)*100, 100, 100);
	}
}

function keyPressed() {
	if(keyCode == ENTER){
		request_labels();
	}
}

function getAllMethods(object) {
    return Object.getOwnPropertyNames(object).filter(function(property) {
        return typeof object[property] == 'function';
    });
}


function request_labels(){
	socket.emit("request_predictions", {text: input.value()});
}

socket.on('receive_predictions', (data) => {
	select('#result').html(data.predictions[0][0]);
	select('#probability').html(nf(data.predictions[0][1], 0, 2));
	meme_scores = data.predictions;
});
