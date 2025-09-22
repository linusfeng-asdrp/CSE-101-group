/**
 * @param {number[][]} grid
 * @return {boolean}
 */
var checkXMatrix = function(grid) {
     const n = grid.length;
    
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            // Check if the element is on a diagonal
            if (i === j || i + j === n - 1) {
                if (grid[i][j] === 0) {
                    return false; // diagonal element must be non-zero
                }
            } else {
                if (grid[i][j] !== 0) {
                    return false; // non-diagonal element must be zero
                }
            }
        }
    }
    
    return true; // all conditions satisfied
    
};
