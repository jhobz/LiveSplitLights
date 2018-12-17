const net = require('net');
const spawn = require('child_process').spawn
let lastBpt = '';
let lastState = '';
let isExecutingScript = false;

const parseData = (data) => {
	data = data.toString().trim();
	if (data.indexOf('\r\n') >= 0) {
		// Two lines of data got sent in one packet
		let lines = data.split('\r\n');
		lines.forEach((line) => {
			parseData(line)
		});
	} else if (!utils.hasNumber(data)) {
		parseState(data);
	} else if (lastState !== 'NotRunning') {
		parseBPT(data);
	}
};

const parseState = (state) => {
	console.log(`parsing state:\nold: ${lastState}\nnew: ${state}\n`);
	if (state === lastState) {
		return;
	}
	if (lastState === 'Running' && state === 'NotRunning') { // Reset
		// TODO: Change this to blink lights
		flashLights('red', 3);
	} else if (lastState === 'NotRunning' && state === 'Running') { // Start timer
		// TODO: Change this to blink lights or custom animation
		flashLights('green', 3);
	}
	lastState = state;
};

const parseBPT = (bpt) => {
	if (bpt === lastBpt) {
		return;
	}
	if (utils.compareTimeStrings(bpt, lastBpt) === '-') {
		console.log('GOLD SPLIT\n', `old: ${lastBpt}\n`, `new: ${bpt}\n`);
		flashLights('gold', 1.5);
	}
	lastBpt = bpt;
}

const flashLights = (color, duration) => {
	if (!isExecutingScript) {
		isExecutingScript = true;
		const py = spawn('python', ['lifxlanwrapper.py', color, `-d ${duration}`])
		py.stdout.on('data', (data) => {
			console.log('Output from python script\r\n', data.toString());
		});

		py.stdout.on('end', () => {
			isExecutingScript = false;
		});
	} else {
		console.log('Ignored light change: Script already executing');
	}
}

const utils = {
	compareTimeStrings: (time1, time2) => {
		let pieces1 = time1.split(/[:.]+/).map(s => Number(s));
		let pieces2 = time2.split(/[:.]+/).map(s => Number(s));

		if (pieces1.length < pieces2.length) {
			return '-';
		} else if (pieces1.length > pieces2.length) {
			return '+';
		}

		function recur(i) {
			if (i === pieces1.length || i === pieces2.length) {
				return '=';
			}
			if (pieces1[i] < pieces2[i]) {
				return '-';
			} else if (pieces1[i] > pieces2[i]) {
				return '+';
			}

			return recur(++i);
		};
		return recur(0);
	},
	hasNumber: (str) => {
		return /\d/.test(str);
	}
};

var client = new net.Socket();
client.connect(16834, 'localhost', () => {
	console.log('Connected');
	setInterval(() => {
		// client.write('getdelta Best Segments\r\n');
		client.write('getcurrenttimerphase\r\n');
		client.write('getbestpossibletime\r\n');
	}, 250);
	// client.write('starttimer\r\n');
});
client.on('data', parseData);
client.on('close', () => {
	console.log('Connection closed.');
});
