/**
 * @param {Function[]} functions
 * @return {Function}
 */
var compose = function(functions) {
    return function(x) {
        // reduce rigth works from right to left
        // intial value of x
        return functions.reduceRight((acc, fn) => fn(acc), x);
    }
    
    return function(x) {
        
    }
