"""Train a simple character-level seq2seq translator for Latin -> target script.

Usage examples:
  python scripts/train_translator.py --dataset data/pairs.csv --target aksara_name

If no dataset provided the script will create a tiny sample using available
aksara modules. The script saves a model under `models/translator.h5` and
tokenizers under `models/tokenizers.pkl`.
"""
import argparse
import os
import sys
import pickle
from typing import List, Tuple

import numpy as np

from tensorflow import keras
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, TimeDistributed
from tensorflow.keras.models import Model

try:
    import pandas as pd
except Exception:
    pd = None

from games.libraries import translator
from games.libraries import ner as ner_lib


def sample_pairs(target: str) -> List[Tuple[str, str]]:
    # fallback sample words
    words = ["satu", "dua", "tiga", "rumah", "air", "mata", "api"]
    pairs = []
    for w in words:
        pairs.append((w, translator.translate_to_script(target, w)))
    return pairs


def load_dataset(path: str, target: str):
    # If dataset is a CSV with latin,target columns
    if path and os.path.exists(path) and pd is not None:
        df = pd.read_csv(path)
        if 'latin' in df.columns and 'target' in df.columns:
            return list(zip(df['latin'].astype(str), df['target'].astype(str)))
    # If path is a text file, use NER to extract words
    if path and os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                txt = f.read()
            resp = ner_lib.analyze_text(txt)
            ents = []
            if resp and resp.get('status') == 200:
                ents = [e['text'] for e in resp['data'].get('entities', [])]
            # fallback to tokenization if no entities
            if not ents:
                ents = [w for w in txt.split() if len(w) > 1][:200]
            return [(w, translator.translate_to_script(target, w)) for w in ents]
        except Exception:
            pass

    # fallback sample pairs
    return sample_pairs(target)


def build_vocab(sequences):
    chars = sorted({ch for s in sequences for ch in s})
    stoi = {c: i + 1 for i, c in enumerate(chars)}  # 0 reserved for padding
    stoi['<s>'] = len(stoi) + 1
    stoi['</s>'] = len(stoi) + 1
    itos = {i: c for c, i in stoi.items()}
    return stoi, itos


def encode_sequences(seqs, stoi, maxlen):
    arr = np.zeros((len(seqs), maxlen), dtype='int32')
    for i, s in enumerate(seqs):
        for j, ch in enumerate(s[:maxlen]):
            arr[i, j] = stoi.get(ch, 0)
    return arr


def make_model(inp_vocab, out_vocab, embed=64, latent=128):
    enc_inputs = Input(shape=(None,), name='enc_in')
    x = Embedding(input_dim=inp_vocab + 1, output_dim=embed, mask_zero=True)(enc_inputs)
    enc_out, state_h, state_c = LSTM(latent, return_state=True)(x)

    dec_inputs = Input(shape=(None,), name='dec_in')
    y = Embedding(input_dim=out_vocab + 1, output_dim=embed, mask_zero=True)(dec_inputs)
    dec_lstm = LSTM(latent, return_sequences=True)
    dec_out = dec_lstm(y, initial_state=[state_h, state_c])
    out = TimeDistributed(Dense(out_vocab + 1, activation='softmax'))(dec_out)

    model = Model([enc_inputs, dec_inputs], out)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
    return model


def prepare_training(pairs):
    inputs = [p[0] for p in pairs]
    outputs = [p[1] for p in pairs]
    inp_stoi, inp_itos = build_vocab(inputs)
    out_stoi, out_itos = build_vocab(outputs)
    max_in = max(len(s) for s in inputs) + 1
    max_out = max(len(s) for s in outputs) + 2

    enc_seq = encode_sequences(inputs, inp_stoi, max_in)
    # decoder input includes start token
    dec_in = [('<s>' + s) for s in outputs]
    dec_out = [(s + '</s>') for s in outputs]
    dec_in_seq = encode_sequences(dec_in, out_stoi, max_out)
    dec_out_seq = encode_sequences(dec_out, out_stoi, max_out)
    # expand dims for sparse categorical crossentropy
    dec_out_seq = np.expand_dims(dec_out_seq, -1)
    return (enc_seq, dec_in_seq, dec_out_seq, inp_stoi, inp_itos, out_stoi, out_itos, max_in, max_out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dataset', default=None)
    p.add_argument('--target', default='jawa')
    p.add_argument('--epochs', type=int, default=10)
    args = p.parse_args()

    pairs = load_dataset(args.dataset, args.target)
    enc_seq, dec_in_seq, dec_out_seq, inp_stoi, inp_itos, out_stoi, out_itos, max_in, max_out = prepare_training(pairs)

    model = make_model(len(inp_stoi), len(out_stoi))
    model.summary()
    model.fit([enc_seq, dec_in_seq], dec_out_seq, epochs=args.epochs, batch_size=16)

    os.makedirs('models', exist_ok=True)
    model.save('models/translator.h5')
    with open('models/tokenizers.pkl', 'wb') as f:
        pickle.dump({'inp_stoi': inp_stoi, 'inp_itos': inp_itos, 'out_stoi': out_stoi, 'out_itos': out_itos, 'max_in': max_in, 'max_out': max_out}, f)
    print('Saved model to models/translator.h5 and tokenizers to models/tokenizers.pkl')


if __name__ == '__main__':
    main()
