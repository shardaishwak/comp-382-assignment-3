/**
 * Compute how well the domnos chain together on top and bottom rows.
 * 
 * Idea: Two adjacent dominos "match" on a row when the last symbol of the left domnio equals the first symbol on the right domino, morning a sort of chain.
 * 
 * Returns: percentage value for the top and bottom
 */

import { Domino } from "./types";

export function computeScores(dominos: Domino[]): {top: number, bottom: number} {
    if (dominos.length < 2) return {top: 0, bottom: 0}

    let topMatches = 0, bottomMatches = 0;
    const pairs = dominos.length - 1;

    for (let i = 0; i < pairs; i++) {
        const right = dominos[i]
        const left = dominos[i+1]

        if (left.top[left.top.length - 1] === right.top[0]) topMatches++;
        if (left.bottom[left.bottom.length - 1] === right.bottom[0]) bottomMatches++;
    }

    return {
        top: Math.round((topMatches / pairs) * 100),
        bottom: Math.round((bottomMatches / pairs) * 100)
    }
}