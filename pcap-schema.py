import pyshark
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

import config
from memory import Memory


class PcapSchema:
    NUMBER_OF_COLORS = 255

    def __init__(self):
        self.pcap_path = config.pcap_path

        # append the custom display-filter to the client-ip filter
        self.client_ip = config.client_ip
        self.display_filter = "ip.addr==" + self.client_ip + " and " + config.display_filter

        self.memory = Memory()
        self.colors = {}
        self.cmap = plt.cm.get_cmap('hsv')

    def build_flows(self):
        pcap = pyshark.FileCapture(self.pcap_path, display_filter=self.display_filter)
        for pkt in pcap:
            self.memory.upsert(pkt)

    def draw_schema(self):

        minimal_timestamp = self.memory.get_minimal_timestamp()

        fig = plt.figure()
        plot = fig.add_subplot(111)

        for flow in self.memory.inner.values():
            xs = []
            ys = []
            for packet in flow.packets:
                xs.append(flow.client.port)
                ys.append(float(packet.sniff_timestamp) - float(minimal_timestamp))
            plot.scatter(xs, ys,
                         label="{}:{} -> {}:{}".format(flow.client.ip, flow.client.port, flow.server.ip,
                                                       flow.server.port),
                         picker=True)

        # fig.canvas.mpl_connect("hover_event", show_flow_info)
        plt.legend()
        plt.show()

    def get_color(self, src_port):

        if src_port not in self.colors:
            self.colors[src_port] = self.cmap(int(src_port) % PcapSchema.NUMBER_OF_COLORS)
        return self.colors[src_port]

    def draw_gantt(self):
        fig, ax = plt.subplots()
        fig.suptitle(self.client_ip)
        ytick_labels = []
        yticks = []
        minimal_timestamp = self.memory.get_minimal_timestamp()
        for i, (four_tuple, flow) in enumerate(self.memory.items()):
            ax.broken_barh([(flow.start_time - minimal_timestamp, flow.end_time - flow.start_time)], (i * 5, 4),
                           facecolors=self.get_color(flow.client.port), picker=True).set_gid(flow)
            ytick_labels.append(str(flow.server))
            yticks.append(i * 5 + 2.5)
        ax.set_xlabel('Seconds')
        ax.set_yticklabels(ytick_labels)
        ax.set_yticks(yticks)
        ax.set_ylabel('External Port')
        plt.legend(title='Internal Port',
                   handles=[mpatches.Patch(color=color, label=src_port) for src_port, color in self.colors.items()])

        def onpick(event):
            print(event.artist.get_gid())

        # tooltip = mpld3.plugins.LineLabelTooltip(fig)
        # mpld3.plugins.connect(fig, tooltip)
        fig.canvas.mpl_connect("pick_event", onpick)
        plt.show()

        # def draw_gantt(self):
        #     df_ = [dict(Task=str(four_tuple), Start=flow.start_time, Finish=flow.end_time) for four_tuple, flow in
        #            self.memory.items()]
        #     df = [dict(Task="Job A", Start=time.strftime('%Y-%d-%m %H:%M:%S', time.gmtime(1505201285.089699000)), Finish=time.strftime('%Y-%d-%m %H:%M:%S', time.gmtime(1505201292.530975000))),
        #           dict(Task="Job B", Start=time.strftime('%Y-%d-%m %H:%M:%S', time.gmtime(1505201285.518623000)), Finish=time.strftime('%Y-%d-%m %H:%M:%S', time.gmtime(1505201285.616012000)))]
        #     print(df)
        #     print(df_)
        #     fig = ff.create_gantt(df)
        #     py.plot(fig, filename='gantt-simple-gantt-chart', world_readable=True)

    def draw_flows(self):
        minimal_timestamp = float(self.memory.get_minimal_timestamp())
        ytick_labels = []
        yticks = []
        fig = plt.figure()
        fig.suptitle(
            self.client_ip + " on " + self.pcap_path[self.pcap_path.rfind("\\\\") + 2: self.pcap_path.rfind(".")])
        ax = fig.add_subplot(111)
        for i, (four_tuple, flow) in enumerate(self.memory.items()):
            ax.plot(np.array([float(t) - minimal_timestamp for t in (flow.start_time, flow.end_time)]),
                    np.array([i * 3] * 2), 'k')
            ax.plot(np.array([float(pkt.sniff_timestamp) - minimal_timestamp for pkt in flow]),
                    np.array([i * 3] * len(flow)), 'bo', color=self.get_color(flow.client.port), picker=True)[
                0].set_gid(
                flow)
            ytick_labels.append(str(flow.server))
            yticks.append(i * 3)
        ax.set_yticks(yticks)
        ax.set_yticklabels(ytick_labels)
        ax.set_xlabel("Seconds since beginning of capture")
        ax.set_ylabel("External IP:Port")
        plt.legend(title='Internal Port',
                   handles=[mpatches.Patch(color=color, label=src_port) for src_port, color in self.colors.items()])

        def onpick(event):
            print(event.artist.get_gid())

        #
        # # tooltip = mpld3.plugins.LineLabelTooltip(fig)
        # # mpld3.plugins.connect(fig, tooltip)
        fig.canvas.mpl_connect("pick_event", onpick)
        plt.show()


if __name__ == "__main__":
    pcap_schema = PcapSchema()
    pcap_schema.build_flows()
    # pcap_schema.draw_gantt()
    pcap_schema.draw_flows()