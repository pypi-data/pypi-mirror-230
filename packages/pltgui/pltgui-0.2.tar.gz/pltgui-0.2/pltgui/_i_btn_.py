#coding=utf-8

"""
一个在plt.ion之后的交互式界面上提供按钮的库
"""


import numpy as np
from matplotlib import pyplot as plt


class i_button:
    """
    按钮类，主要负责画按钮，以及获取和设置按钮的部分信息
    """

    def __init__(
            self,
            ax, ct_x, ct_y, wid, hei,
            color, text, cmd,
            action=None,
            fill=True, chk_color=None, chk_text=None):
        """
        在画布上画一个按钮出来
        :param ax: 画布对象
        :param ct_x, ct_y: 中心坐标
        :param wid, hei: 宽度和高度（全宽、全高）
        :param color: 按钮的背景颜色
        :param text: 按钮文字
        :param cmd: 按钮命令关键字
        :param action: 按钮的回调函数，
        :param fill: 如果为真，则绘制一个实心的盒子，否则是空心的
        :param chk_color: 当按钮打标签的时候的颜色
        :param chk_text: 当按钮打标签的时候的文字
        """
        # 保存信息
        self.ax    = ax
        self.ct_x  = ct_x
        self.ct_y  = ct_y
        self.wid   = wid
        self.hei   = hei
        self.cmd   = cmd
        self._color_ = color
        self._text_ = text
        self.action = action
        self.fill  = fill
        self._chked_ = False
        self.chk_color = chk_color if chk_color else color
        self.chk_text  = chk_text if chk_text else text
        # 计算x和y边界（内部用）
        xr = self._xr_ = np.array([-0.5, 0.5]) * wid + ct_x
        yr = self._yr_ = np.array([-0.5, 0.5]) * hei + ct_y
        # 画图
        self._p_box_ = ax.fill(xr[[0,1,1,0]], yr[[0,0,1,1]], color=color, fill=fill)[0]
        # 如果是实心的，写在中心，颜色是黑色，否则就写到右上角
        if fill:
            self._p_txt_ = ax.text(ct_x, ct_y, text, color="k", ha="center", va="center")
        else:
            self._p_txt_ = ax.text(ct_x + wid / 2, ct_y + hei / 2, text, color=color, ha="left", va="bottom")

    @property
    def text(self):
        """
        读取文字的属性
        """
        return self._text_

    @text.setter
    def text(self, text):
        """
        文字属性的写函数
        """
        self._text_ = text
        self._p_txt_.set_text(text)

    @property
    def color(self):
        """
        读取背景颜色的属性
        """
        return self._color_

    @color.setter
    def color(self, color):
        """
        颜色属性的写函数
        """
        self._color_ = color
        self._p_box_.set_color(color)
        if not self.fill:
            self._p_txt_.set_color(color)

    @property
    def chked(self):
        """
        读取是否打标签
        :return:
        """
        return self._chked_

    @chked.setter
    def chked(self, c):
        """
        设置标签状态
        :param c:
        :return:
        """
        self._chked_ = c
        if c:
            self._p_txt_.set_text(self.chk_text)
            self._p_box_.set_color(self.chk_color)
        else:
            self._p_txt_.set_text(self._text_)
            self._p_box_.set_color(self._color_)

    def check(self):
        """
        直接打标签
        :return:
        """
        self.chked = True

    def uncheck(self):
        """
        直接取消标签
        :return:
        """
        self.chked = False

    def toggle_check(self):
        """
        直接标签状态反转
        :return:
        """
        self.chked = not self.chked

    def remove(self):
        """
        删除自己，但是在按钮管理器中的记录需要另外删
        """
        self._p_box_.remove()
        self._p_txt_.remove()


class i_btn_ctl:
    """
    按钮管理器，需要维持一个按钮列表，以及识别是哪个按钮被按到了
    """
    
    def __init__(self, ax):
        # 画布
        self.ax = ax
        self.fig = ax.figure
        # 按钮数组
        self.btns = []
        # 记录按钮的左、右、上、下界限
        self._range_l_ = []
        self._range_r_ = []
        self._range_t_ = []
        self._range_b_ = []
    
    def add_btn(self, ct_x, ct_y, wid, hei, bgc, text, cmd, action=None, fill=True, chk_color=None, chk_text=None):
        """
        添加按钮，参数都是按钮的
        """
        # 添加按钮
        bb = i_button(self.ax, ct_x, ct_y, wid, hei, bgc, text, cmd, action, fill, chk_color, chk_text)
        # 按钮加入列表
        self.btns.append(bb)
        # 记录其四界
        self._range_l_.append(bb._xr_[0])
        self._range_r_.append(bb._xr_[1])
        self._range_b_.append(bb._yr_[0])
        self._range_t_.append(bb._yr_[1])
        return bb

    def remove_btn(self, btn):
        """
        删除指定按钮，同时要删除边界信息
        """
        # 找到按钮
        i = self.btns.index(btn)
        # 如果找到就删除
        if 0 <= i < len(self.btns):
            btn.remove()
            del self.btns[i]
            del self._range_l_[i]
            del self._range_r_[i]
            del self._range_t_[i]
            del self._range_b_[i]

    def clear(self):
        """
        删除所有按钮
        :return:
        """
        for b in self.btns:
            b.remove()
        self.btns.clear()
        self._range_l_.clear()
        self._range_r_.clear()
        self._range_t_.clear()
        self._range_b_.clear()

    def set_axis_lim(self, padding=0.1):
        """
        对于专门用于部署按钮的ax，根据按钮情况，设置画布的四界，并且关闭坐标轴显示
        对于按钮和其他操作对象混合在一起的模式，不宜用本函数
        :param padding: 按钮之外和画框保持的距离，实际宽度的倍数
        """
        # 根据所有按钮的上下左右边界，计算总的外框
        xlim_l = min(self._range_l_)
        xlim_r = max(self._range_r_)
        ylim_t = max(self._range_t_)
        ylim_b = min(self._range_b_)
        # 定义一个计算线性外展的函数
        ext = lambda u, v, f: u * (1-f) + v * f
        # 向外适当扩展，设置画布大小
        self.ax.set_xlim(ext(xlim_l, xlim_r, -padding), ext(xlim_l, xlim_r, 1+padding))
        self.ax.set_ylim(ext(ylim_b, ylim_t, -padding), ext(ylim_b, ylim_t, 1+padding))
        # 关闭坐标轴
        self.ax.set_axis_off()

    def locate(self, x, y):
        """
        根据xy坐标看落在哪个按钮的区域内，也可能不再任何一个按钮内
        :param x, y: 点击坐标
        :return: 按钮，或者None
        """
        # 根据四界去判断xy是否在某个按钮区域内
        inside = (
            (np.array(self._range_l_) <= x) &
            (np.array(self._range_r_) >= x) &
            (np.array(self._range_b_) <= y) &
            (np.array(self._range_t_) >= y)
        )
        # 找满足条件的按钮，如果只有1个按钮满足，那就是它
        # 如果一个都没有（在所有按钮之外，甚至其它ax），或者按钮之间有重叠，当做没按到
        i = np.where(inside)[0]
        if len(i) == 1:
            btn = self.btns[i[0]]
        else:
            btn = None
        return btn

    def wait_click(self, timeout=1):
        """
        接收用户在图上点击，判断是否按了按钮，返回按钮、按钮命令、点击位置
        :param timeout: 默认超时时间，在此之前没有点击就返回空
        :return: 按钮、按钮命令、点击x、点击y
        """
        # 从图上获取一个点
        p = self.fig.ginput(timeout=timeout)
        # 默认是1秒超时，超时之后会返回空列表，超时就直接跳过
        if p:
            px, py = p[0]
            # 转换成按钮，并获取按钮的命令
            btn = self.locate(px, py)
            # 如果选中了按钮，那么获取按钮的命令，否则命令为空
            c = btn.cmd if btn else ""
        else:
            px, py = None, None
            btn, c = None, ""
        return btn, c, px, py

    def action_loop(self, timeout=1, button_action=None, image_action=None, loop_action=None):
        """
        操作循环，一个无限循环地接受点击和执行操作的函数，参数主要是超时和默认处理函数
        假如点了按钮，并且按钮有自带事件函数，调自带的，否则调按钮默认处理函数，按钮作为参数
        假如点了图像位置，按钮为空，那么调图像点击函数
        如果啥都没点，超时返回，那么调研默认处理函数
        如果某一步没有指定函数（None），那么不处理
        :param timeout: 按钮检测超时秒数
        :param button_action: 假如点击的按钮没有自带的处理函数，那么调研该函数，必须有个参数是按钮
        :param image_action: 假如点击的是图像区域，不是按钮，调研这个，参数x、y
        :param loop_action: 假如超时没点击，执行本函数
        :return: nothing
        """
        # 先假设要无限循环。每一步的返回值如果不是空或者False，就表示要结束循环了
        done = False
        while not done:
            # 接收点击
            b, c, px, py = self.wait_click(timeout=timeout)
            if b:
                done = b.action() if b.action else (button_action(b) if button_action else None)
            elif px:
                done = image_action(px, py) if image_action else None
            else:
                done = loop_action() if loop_action else None
