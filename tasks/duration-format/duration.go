package durationformat

import "strconv"

// FormatSeconds renders a whole number of seconds as compact duration text.
// Negative inputs return "invalid", zero returns "0s", and positive inputs are
// decomposed greedily into days, hours, minutes and seconds.
func FormatSeconds(seconds int64) string {
	if seconds < 0 {
		return "invalid"
	}
	if seconds == 0 {
		return "0s"
	}

	type part struct {
		value int64
		unit  string
	}
	parts := []part{
		{86400, "d"},
		{3600, "h"},
		{60, "m"},
		{1, "s"},
	}

	out := make([]byte, 0, 32)
	remaining := seconds
	first := true
	for _, p := range parts {
		n := remaining / p.value
		remaining %= p.value
		if n == 0 {
			continue
		}
		if !first {
			out = append(out, ' ')
		}
		first = false
		out = append(out, strconv.FormatInt(n, 10)...)
		out = append(out, p.unit...)
	}
	return string(out)
}
