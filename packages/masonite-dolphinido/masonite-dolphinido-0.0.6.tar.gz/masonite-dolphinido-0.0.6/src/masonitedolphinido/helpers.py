import itertools
from termcolor import colored


def grouper(iterable, n, fillvalue=None):
	args = [iter(iterable)] * n
	return (filter(None, params) for params in itertools.zip_longest(fillvalue=fillvalue, *args))

def output(match):
	if match:
		msg = 'Match Found \n \n'
		msg += 'Audio ID: %s \n'
		msg += 'Title: %s \n'
		msg += 'Artist: %s \n'
		msg += 'Offset: %d \n'
		msg += 'Offset Seconds : %d secs \n'
		msg += 'Confidence: %d'

		print("#" * 40)
		print(colored(msg, 'green') % (
			match.audio.id,
			match.audio.metadata.title,
			match.audio.metadata.artist,
			match.offset,
			match.offset_seconds,
			match.confidence
		))
		print("#" * 40)
	else:
		msg = ' ** No matches found'
		print(colored(msg, 'red'))

