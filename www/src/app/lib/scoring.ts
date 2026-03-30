/**
 * Compute how close the placed dominos are to a PCP solution.
 *
 * PCP goal: concatenation of all top symbols === concatenation of all bottom symbols.
 *
 * We measure two things:
 *  - prefixMatch: longest common prefix as % of the longer string (strict PCP progress)
 *  - overallMatch: total position-wise matches as % of the longer string (general feedback)
 *
 * A perfect score (100%) on both means the top and bottom are identical → PCP solved.
 */

import { Domino, Symbol } from "./types";

export function computeScores(dominos: Domino[]): {
    prefixMatch: number;   // percentage (0–100) — strict LCP
    overallMatch: number;  // percentage (0–100) — position-wise matches
    topConcat: Symbol[];
    bottomConcat: Symbol[];
    prefixLen: number;
} {
    if (dominos.length === 0) return { prefixMatch: 0, overallMatch: 0, topConcat: [], bottomConcat: [], prefixLen: 0 }

    const topConcat: Symbol[] = dominos.flatMap(d => d.top)
    const bottomConcat: Symbol[] = dominos.flatMap(d => d.bottom)

    const maxLen = Math.max(topConcat.length, bottomConcat.length)
    const minLen = Math.min(topConcat.length, bottomConcat.length)

    let prefixLen = 0
    while (prefixLen < minLen && topConcat[prefixLen] === bottomConcat[prefixLen]) {
        prefixLen++
    }

    let totalMatches = 0
    for (let i = 0; i < minLen; i++) {
        if (topConcat[i] === bottomConcat[i]) totalMatches++
    }

    const prefixMatch = maxLen > 0 ? Math.round((prefixLen / maxLen) * 100) : 0
    const overallMatch = maxLen > 0 ? Math.round((totalMatches / maxLen) * 100) : 0

    return { prefixMatch, overallMatch, topConcat, bottomConcat, prefixLen }
}