def sum_digits_repeatedly(num, limit):
    if num > limit:
        return "Number too large"
    while num >= 10:
        digit_sum = 0
        while num > 0:
            digit_sum += num % 10
            num //= 10
        num = digit_sum
    return str(num)
print(sum_digits_repeatedly(213498, 2 ** 31 - 1))