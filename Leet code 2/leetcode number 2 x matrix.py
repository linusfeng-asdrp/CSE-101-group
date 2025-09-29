class Solution(object):
    def checkXMatrix(self, grid):
        """
        :type grid: List[List[int]]
        :rtype: bool
        """
        for row in range(len(grid)):
            for column in range(len(grid)):
                if row == column or row == len(grid) - 1 - column:
                    if grid[row][column] == 0:
                        return False
                else:
                    if grid[row][column] != 0:
                        return False
        return True
