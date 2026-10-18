package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"net"
	"os"
	"strconv"
	"time"
)

type Result struct {
	Host      string  `json:"host"`
	Port      int     `json:"port"`
	Address   string  `json:"address"`
	ElapsedMS float64 `json:"elapsed_ms"`
	Error     string  `json:"error,omitempty"`
}

func resolve(ctx context.Context, host string) (string, error) {
	addresses, err := net.DefaultResolver.LookupHost(ctx, host)
	if err != nil {
		return "", err
	}
	if len(addresses) == 0 {
		return "", fmt.Errorf("no addresses returned")
	}
	return addresses[0], nil
}

func check(ctx context.Context, address string) (float64, error) {
	start := time.Now()
	connection, err := (&net.Dialer{}).DialContext(ctx, "tcp", address)
	elapsed := float64(time.Since(start).Microseconds()) / 1000

	if err != nil {
		return elapsed, err
	}
	defer connection.Close()

	return elapsed, nil
}

func run(host string, port int, timeout time.Duration) Result {
	result := Result{Host: host, Port: port}
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	address, err := resolve(ctx, host)
	if err != nil {
		result.Error = err.Error()
		return result
	}

	result.Address = address
	result.ElapsedMS, err = check(ctx, net.JoinHostPort(address, strconv.Itoa(port)))
	if err != nil {
		result.Error = err.Error()
	}

	return result
}

func main() {
	host := flag.String("host", "", "Hostname or IP address")
	port := flag.Int("port", 443, "TCP port")
	timeout := flag.Float64("timeout", 3, "Timeout in seconds")
	flag.Parse()

	if *host == "" || *port < 1 || *port > 65535 ||
		*timeout < 0.1 || *timeout > 30 {
		fmt.Fprintln(os.Stderr, "Provide a host, valid port, and timeout.")
		os.Exit(2)
	}

	result := run(*host, *port, time.Duration(*timeout*float64(time.Second)))
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetEscapeHTML(true)

	if err := encoder.Encode(result); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	if result.Error != "" {
		os.Exit(1)
	}
}
