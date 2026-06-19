"""Run inference with the trained translator model."""
import argparse
import os
import sys
import pickle
import numpy as np
from tensorflow import keras



def load_resources(model_path='models/translator.h5', toks_path='models/tokenizers.pkl'):
    model = keras.models.load_model(model_path)
    with open(toks_path, 'rb') as f:
        toks = pickle.load(f)
    return model, toks


def greedy_decode(model, toks, inp_text):
    inp_stoi = toks['inp_stoi']
    out_stoi = toks['out_stoi']
    out_itos = toks['out_itos']
    max_in = toks['max_in']
    max_out = toks['max_out']

    # encode input
    enc = np.zeros((1, max_in), dtype='int32')
    for i, ch in enumerate(inp_text[:max_in]):
        enc[0, i] = inp_stoi.get(ch, 0)

    # start token
    dec_in = np.zeros((1, max_out), dtype='int32')
    dec_in[0, 0] = out_stoi.get('<s>', 0)

    preds = model.predict([enc, dec_in])
    # greedy read
    out_chars = []
    for t in range(preds.shape[1]):
        token_id = int(preds[0, t].argmax())
        ch = out_itos.get(token_id, '')
        if ch == '</s>':
            break
        if ch not in ('<s>', ''):
            out_chars.append(ch)
    return ''.join(out_chars)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', default='models/translator.h5')
    p.add_argument('--toks', default='models/tokenizers.pkl')
    p.add_argument('text')
    args = p.parse_args()

    model, toks = load_resources(args.model, args.toks)
    out = greedy_decode(model, toks, args.text)
    print(out)


if __name__ == '__main__':
    main()
