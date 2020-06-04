/*
 * Copyright (C) 2013, 2016 Bastian Bloessl <bloessl@ccs-labs.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <ieee802_11/parse_meta_mac.h>
#include "utils.h"

#include <gnuradio/io_signature.h>
#include <gnuradio/block_detail.h>
#include <string>

using namespace gr::ieee802_11;

class parse_meta_mac_impl : public parse_meta_mac {

public:

parse_meta_mac_impl(bool log, bool debug) :
		block("parse_meta_mac",
				gr::io_signature::make(0, 0, 0),
				gr::io_signature::make(0, 0, 0)),
		d_log(log), d_last_seq_no(-1),
		d_debug(debug) {

	message_port_register_in(pmt::mp("in"));
	set_msg_handler(pmt::mp("in"), boost::bind(&parse_meta_mac_impl::parse, this, _1));

	message_port_register_out(pmt::mp("fer"));
}

~parse_meta_mac_impl() {

}
void parse_meta_data(const pmt::pmt_t& dict, mac_header* macHeader)
{
    if(!pmt::is_dict(dict))
      return;

    double snr = 0;
    if(pmt::dict_has_key(dict, pmt::mp("snr"))) {
        pmt::pmt_t value = pmt::dict_ref(dict, pmt::mp("snr"), pmt::PMT_NIL);
        if(pmt::is_number(value)) {
            snr = pmt::to_double(value);
        }
    }
    double freq = 0;
    if(pmt::dict_has_key(dict, pmt::mp("nomfreq"))) {
        pmt::pmt_t value = pmt::dict_ref(dict, pmt::mp("nomfreq"), pmt::PMT_NIL);
            if(pmt::is_number(value)) {
                freq = pmt::to_double(value);
            }
    }
    double freqof = 0;
    if(pmt::dict_has_key(dict, pmt::mp("freqofs"))) {
        dout << "has Key freqofs" << pmt::dict_keys(dict) << std::endl;
        pmt::pmt_t value = pmt::dict_ref(dict, pmt::mp("freqofs"), pmt::PMT_NIL);
        if(pmt::is_number(value)) {
            freqof = pmt::to_double(value);
        }
    }
    else{
        dout << "no Key freqofs: " << pmt::dict_keys(dict) << std::endl;
    }
    std::string data;
    data.append("time: ");
    data.append(std::to_string(std::time(nullptr)));
    data.append("mac1: ");
    data.append(get_mac_string(macHeader->addr1));
    data.append("mac2: ");
    data.append(get_mac_string(macHeader->addr2));
    data.append("mac3: ");
    data.append(get_mac_string(macHeader->addr3));
    data.append("snr: ");
    data.append(std::to_string(snr));
    data.append(";freq: ");
    data.append(std::to_string(freq));
    data.append(";freqof: ");
    data.append(std::to_string(freqof));
    /*
    pmt::pmt_t vec = pmt::make_f64vector(3, 8.0);
    pmt::f64vector_set(vec, 0, snr);
+   pmt::f64vector_set(vec, 1, freq);
    pmt::f64vector_set(vec, 2, freqof);
     */

    dout << data << std::endl;
    std::size_t data_len = sizeof(data.c_str()[0]) * data.size();
    message_port_pub(pmt::mp("fer"), pmt::cons( pmt::PMT_NIL,  pmt::make_blob(data.c_str(), data_len)));
    dout << "After PUB" << std::endl;
}

std::string get_mac_string(uint8_t *addr) const
{
    std::stringstream stream;
    stream << std::setfill('0') << std::hex << std::setw(2);

    for(int i = 0; i < 6; i++) {
        stream << (int)addr[i];
        if(i != 5) {
            stream << ":";
        }
    }

    return stream.str();
}

void parse(pmt::pmt_t msg) {

	if(pmt::is_eof_object(msg)) {
		detail().get()->set_done(true);
		return;
	} else if(pmt::is_symbol(msg)) {
		return;
	}

	pmt::pmt_t dict = pmt::car(msg);

	msg = pmt::cdr(msg);

	mac_header* header = (mac_header*)pmt::blob_data(msg);

	dout << "Dict: " << pmt::dict_keys(dict) << std::endl;
	parse_meta_data(dict, header);

}

private:
	bool d_log;
	bool d_debug;
	int d_last_seq_no;
};

parse_meta_mac::sptr
parse_meta_mac::make(bool log, bool debug) {
	return gnuradio::get_initial_sptr(new parse_meta_mac_impl(log, debug));
}
